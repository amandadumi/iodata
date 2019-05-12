# IODATA is an input and output module for quantum chemistry.
# Copyright (C) 2011-2019 The IODATA Development Team
#
# This file is part of IODATA.
#
# IODATA is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# IODATA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""Module for handling MOLEKEL file format."""


from typing import Tuple, List

import numpy as np

from .molden import CONVENTIONS, _fix_molden_from_buggy_codes
from ..basis import angmom_sti, MolecularBasis, Shell
from ..orbitals import MolecularOrbitals
from ..utils import angstrom, LineIterator


__all__ = []


patterns = ['*.mkl']


def _load_helper_charge_spinpol(lit: LineIterator) -> List[int]:
    charge, spinmult = [int(word) for word in next(lit).split()]
    spinpol = spinmult - 1
    return charge, spinpol


def _load_helper_atoms(lit: LineIterator) -> Tuple[np.ndarray, np.ndarray]:
    atnums = []
    atcoords = []
    for line in lit:
        if line.strip() == '$END':
            break
        words = line.split()
        atnums.append(int(words[0]))
        atcoords.append([float(words[1]), float(words[2]), float(words[3])])
    atnums = np.array(atnums, int)
    atcoords = np.array(atcoords) * angstrom
    return atnums, atcoords


def _load_helper_obasis(lit: LineIterator) -> MolecularBasis:
    shells = []
    icenter = 0
    while True:
        line = next(lit).strip()
        if line == '$END':
            break
        if line == "":
            continue
        if line == '$$':
            icenter += 1
            continue
        # Shell header, always assuming pure functions
        words = line.split()
        angmom = angmom_sti(words[1])
        nbasis_shell = int(words[0])
        if nbasis_shell == len(CONVENTIONS[(angmom, 'c')]):
            kind = 'c'
        elif nbasis_shell == len(CONVENTIONS[(angmom, 'p')]):
            kind = 'p'
        else:
            lit.error('Cannot interpret angmom={} with nbasis_shell={}'.format(
                angmom, nbasis_shell))
        exponents = []
        coeffs = []
        for line in lit:
            words = line.split()
            if len(words) != 2:
                lit.back(line)
                break
            exponents.append(float(words[0]))
            coeffs.append([float(words[1])])
        shells.append(Shell(icenter, [angmom], [kind], np.array(exponents), np.array(coeffs)))
    return MolecularBasis(shells, CONVENTIONS, 'L2')


def _load_helper_coeffs(lit: LineIterator, nbasis: int) -> Tuple[np.ndarray, np.ndarray]:
    coeffs = []
    energies = []

    in_orb = 0
    for line in lit:
        line = line.strip()
        if line == '$END':
            break
        if in_orb == 0:
            # read a1g line
            words = line.split()
            ncol = len(words)
            assert ncol > 0
            for word in words:
                assert word == 'a1g'
            cols = [np.zeros((nbasis, 1), float) for _ in range(ncol)]
            in_orb = 1
        elif in_orb == 1:
            # read energies
            words = line.split()
            assert len(words) == ncol
            for word in words:
                energies.append(float(word))
            in_orb = 2
            ibasis = 0
        elif in_orb == 2:
            # read expansion coefficients
            words = line.split()
            assert len(words) == ncol
            for icol in range(ncol):
                cols[icol][ibasis] = float(words[icol])
            ibasis += 1
            if ibasis == nbasis:
                in_orb = 0
                coeffs.extend(cols)

    return np.hstack(coeffs), np.array(energies)


def _load_helper_occ(lit: LineIterator) -> np.ndarray:
    occs = []
    for line in lit:
        line = line.strip()
        if line == '$END':
            break
        for word in line.split():
            occs.append(float(word))
    return np.array(occs)


# pylint: disable=too-many-branches,too-many-statements
def load_one(lit: LineIterator) -> dict:
    """Load data from a MOLEKEL file format.

    Parameters
    ----------
    lit
        The line iterator to read the data from.

    Returns
    -------
    out
        Output dictionary containing ``atcoords``, ``atnums``, ``obasis``, ``mo``,
        keys and their corresponding values.

    """
    charge = None
    atnums = None
    atcoords = None
    obasis = None
    coeff_alpha = None
    ener_alpha = None
    occ_alpha = None
    coeff_beta = None
    ener_beta = None
    occ_beta = None
    # Using a loop because we're not entirely sure if sections in an MKL file
    # have a fixed order.
    while True:
        try:
            line = next(lit).strip()
        except StopIteration:
            # There is no file-end marker we can use, so we only stop when
            # reaching the end of the file.
            break
        if line == '$CHAR_MULT':
            charge, spinpol = _load_helper_charge_spinpol(lit)
        elif line == '$COORD':
            atnums, atcoords = _load_helper_atoms(lit)
        elif line == '$BASIS':
            obasis = _load_helper_obasis(lit)
        elif line == '$COEFF_ALPHA':
            coeff_alpha, ener_alpha = _load_helper_coeffs(lit, obasis.nbasis)
        elif line == '$OCC_ALPHA':
            occ_alpha = _load_helper_occ(lit)
        elif line == '$COEFF_BETA':
            coeff_beta, ener_beta = _load_helper_coeffs(lit, obasis.nbasis)
        elif line == '$OCC_BETA':
            occ_beta = _load_helper_occ(lit)

    if charge is None:
        lit.error('Charge and spin polarization not found.')
    if atcoords is None:
        lit.error('Coordinates not found.')
    if obasis is None:
        lit.error('Orbital basis not found.')
    if coeff_alpha is None:
        lit.error('Alpha orbitals not found.')
    if occ_alpha is None:
        lit.error('Alpha occupation numbers not found.')

    nelec = atnums.sum() - charge
    if coeff_beta is None:
        # restricted closed-shell
        mo_type = 'restricted'
        assert nelec % 2 == 0
        assert abs(occ_alpha.sum() - nelec) < 1e-7
        norba = norbb = coeff_alpha.shape[1]
        mo_occs = occ_alpha
        mo_coeffs = coeff_alpha
        mo_energy = ener_alpha
    else:
        mo_type = 'unrestricted'
        if occ_beta is None:
            lit.error('Beta occupation numbers not found in mkl file while '
                      'beta orbitals were present.')
        nalpha = int(np.round(occ_alpha.sum()))
        nbeta = int(np.round(occ_beta.sum()))
        assert abs(spinpol - abs(nalpha - nbeta)) < 1e-7
        assert nelec == nalpha + nbeta
        assert coeff_alpha.shape == coeff_beta.shape
        assert ener_alpha.shape == ener_beta.shape
        assert occ_alpha.shape == occ_beta.shape
        norba = coeff_alpha.shape[1]
        norbb = coeff_beta.shape[1]
        mo_occs = np.concatenate((occ_alpha, occ_beta), axis=0)
        mo_energy = np.concatenate((ener_alpha, ener_beta), axis=0)
        mo_coeffs = np.concatenate((coeff_alpha, coeff_beta), axis=1)
    # create a MO namedtuple
    mo = MolecularOrbitals(mo_type, norba, norbb, mo_occs, mo_coeffs, None, mo_energy)

    result = {
        'atcoords': atcoords,
        'atnums': atnums,
        'obasis': obasis,
        'mo': mo,
    }
    _fix_molden_from_buggy_codes(result, lit.filename)
    return result
