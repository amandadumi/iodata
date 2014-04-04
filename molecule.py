# -*- coding: utf-8 -*-
# Horton is a development platform for electronic structure methods.
# Copyright (C) 2011-2013 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Horton.
#
# Horton is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Horton is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
#--
'''Input/output dispatcher for different file formats

   The ``Molecule.from_file`` and ``Molecule.to_file`` functions read/write
   molecule data from/to a file. The format is deduced from the prefix or
   extension of the filename.
'''


from horton.matrix import DenseLinalgFactory, LinalgObject
import h5py as h5, os, numpy as np


__all__ = ['Molecule']


class ArrayTypeCheckDescriptor(object):
    def __init__(self, name, ndim=None, shape=None, dtype=None, matching=None, default=None):
        '''
           Decorator to perform type checking an np.ndarray attributes

           **Arguments:**

           name
                Name of the attribute (without leading underscores).

           **Optional arguments:**

           ndim
                The number of dimensions of the array.

           shape
                The shape of the array. Use -1 for dimensions where the shape is
                not fixed a priori.

           dtype
                The datype of the array.

           matching
                A list of names of other attributes that must have consistent
                shapes. This argument requires that the shape is speciefied.
                All dimensions for which the shape tuple equals -1 are must be
                the same in this attribute and the matching attributes.

           default
                The name of another (type-checke) attribute to return as default
                when this attribute is not set
        '''
        if matching is not None and shape is None:
            raise TypeError('The matching argument requires the shape to be '
                            'specified.')
        self._name = name
        self._ndim = ndim
        self._shape = shape
        if dtype is None:
            self._dtype = None
        else:
            self._dtype = np.dtype(dtype)
        self._matching = matching
        self._default = default

    def __get__(self, obj, type=None):
        if self._default is not None and not hasattr(obj, '_' + self._name):
            return getattr(obj, '_' + self._default).astype(self._dtype)
        return getattr(obj, '_' + self._name)

    def __set__(self, obj, value):
        # try casting to proper dtype:
        value = np.array(value, dtype=self._dtype, copy=False)
        #if not isinstance(value, np.ndarray):
        #    raise TypeError('Attribute \'%s\' of \'%s\' must be a numpy '
        #                    'array.' % (self._name, type(obj)))
        if self._ndim is not None and value.ndim != self._ndim:
            raise TypeError('Attribute \'%s\' of \'%s\' must be a numpy array '
                            'with %i dimension(s).' % (self._name, type(obj),
                            self._ndim))
        if self._shape is not None:
            for i in xrange(len(self._shape)):
                if self._shape[i] >= 0 and self._shape[i] != value.shape[i]:
                    raise TypeError('Attribute \'%s\' of \'%s\' must be a numpy'
                                    ' array %i elements in dimension %i.' % (
                                    self._name, type(obj), self._shape[i], i))
        if self._dtype is not None:
            if not issubclass(value.dtype.type, self._dtype.type):
                raise TypeError('Attribute \'%s\' of \'%s\' must be a numpy '
                                'array with dtype \'%s\'.' % (self._name,
                                type(obj), self._dtype.type))
        if self._matching is not None:
            for othername in self._matching:
                other = getattr(obj, '_'+othername, None)
                if other is not None:
                    for i in xrange(len(self._shape)):
                        if self._shape[i] == -1 and \
                           other.shape[i] != value.shape[i]:
                            raise TypeError('shape[%i] of attribute \'%s\' of '
                                            '\'%s\' in is incompatible with '
                                            'that of \'%s\'.' % (i, self._name,
                                            type(obj), othername))
        setattr(obj, '_'+self._name, value)

    def __delete__(self, obj):
        delattr(obj, '_'+self._name)


class Molecule(object):
    '''A container class for data loaded from (or to be written to) a file.

       In principle, the constructor accepts any keyword argument, which is
       stored as an attribute. All attributes are optional. Attributes can be
       set are removed after the molecule is constructed. The following
       attributes are supported by at least one of the io formats:

       **Type checked array attributes (if present):**

       cube_data
            A (L, M, N) array of data on a uniform grid (defined by ugrid).

       coordinates
            A (N, 3) float array with Cartesian coordinates of the atoms.

       numbers
            A (N,) int vector with the atomic numbers.

       pseudo_numbers
            A (N,) float array with pseudo-potential core charges.

       **Unspecified type (duck typing):**

       cell
            A Cell object that describes the (generally triclinic) periodic
            boundary conditions.

       energy
            The total energy (electronic+nn) of the molecule

       er
            The electron repulsion two-body operator

       exp_alpha
            The alpha orbitals (coefficients, occupations and energies)

       exp_beta
            The beta orbitals (coefficients, occupations and energies)

       esp_charges
            Charges fitted to the electrostatic potential

       dm_full (optionally with some prefix like _mp2, _mp3, _cc, _ci, _scf).
            The spin-summed first-order density matrix

       dm_spin (optionally with some prefix like _mp2, _mp3, _cc, _ci, _scf).
            The spin-difference first-order density matrix

       grid
            An integration grid (usually a UniformGrid instance)

       kin
            The kinetic energy operator

       lf
            A LinalgFactory instance.

       mulliken_charges
            Mulliken AIM charges

       na
            The nuclear attraction operator

       npa_charges
            Natural charges

       obasis
            An instance of the GOBasis class.

       olp
            The overlap operator

       permutation
            The permutation applied to the basis functions.

       signs
            The sign changes applied to the basis functions.

       symmetry
            An instance of the Symmetry class, describing the geometric
            symmetry.

       links
            A mapping between the atoms in the primitive unit and the
            crystallographic unit.
    '''
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    # only perform type checking on minimal attributes
    numbers = ArrayTypeCheckDescriptor('numbers', 1, (-1,), int, ['coordinates', 'pseudo_numbers'])
    coordinates = ArrayTypeCheckDescriptor('coordinates', 2, (-1, 3), float, ['numbers', 'pseudo_numbers'])
    pseudo_numbers = ArrayTypeCheckDescriptor('pseudo_numbers', 1, (-1,), float, ['coordinates', 'numbers'], 'numbers')
    cube_data = ArrayTypeCheckDescriptor('cube_data', 3)

    def _get_natom(self):
        '''The number of atoms'''
        if hasattr(self, 'numbers'):
            return len(self.numbers)
        elif hasattr(self, 'coordinates'):
            return len(self.coordinates)
        elif hasattr(self, 'pseudo_numbers'):
            return len(self.pseudo_numbers)

    natom = property(_get_natom)

    @classmethod
    def from_file(cls, *filenames, **kwargs):
        '''Load a molecule from a file.

           **Arguments:**

           filename1, filename2, ...
                The files to load molecule data from. When multiple files are given,
                data from the first file is overwritten by data from the second,
                etc. When one file contains sign and permutation changes for the
                orbital basis, these changes will be applied to data from all other
                files.

           **Optional arguments:**

           lf
                A LinalgFactory instance. DenseLinalgFactory is used as default.

           This routine uses the extension or prefix of the filename to determine the file
           format. It returns a dictionary with data loaded from the file.

           For each file format, a specialized load_xxx function is called that
           returns a dictionary with data from the file.
        '''
        result = {}

        lf = kwargs.pop('lf', None)
        if lf is None:
            lf = DenseLinalgFactory()
        if len(kwargs) > 0:
            raise TypeError('Keyword argument(s) not supported: %s' % lf.keys())

        for filename in filenames:
            if isinstance(filename, h5.Group) or filename.endswith('.h5'):
                from horton.io.internal import load_h5
                result.update(load_h5(filename, lf))
            elif filename.endswith('.xyz'):
                from horton.io.xyz import load_xyz
                result.update(load_xyz(filename))
            elif filename.endswith('.fchk'):
                from horton.io.gaussian import load_fchk
                result.update(load_fchk(filename, lf))
            elif filename.endswith('.log'):
                from horton.io.gaussian import load_operators_g09
                result.update(load_operators_g09(filename, lf))
            elif filename.endswith('.mkl'):
                from horton.io.molekel import load_mkl
                result.update(load_mkl(filename, lf))
            elif filename.endswith('.molden.input'):
                from horton.io.molden import load_molden
                result.update(load_molden(filename, lf))
            elif filename.endswith('.cube'):
                from horton.io.cube import load_cube
                result.update(load_cube(filename))
            elif filename.endswith('.wfn'):
                from horton.io.wfn import load_wfn
                result.update(load_wfn(filename, lf))
            elif os.path.basename(filename).startswith('POSCAR'):
                from horton.io.vasp import load_poscar
                result.update(load_poscar(filename))
            elif os.path.basename(filename)[:6] in ['CHGCAR', 'AECCAR']:
                from horton.io.vasp import load_chgcar
                result.update(load_chgcar(filename))
            elif os.path.basename(filename).startswith('LOCPOT'):
                from horton.io.vasp import load_locpot
                result.update(load_locpot(filename))
            elif filename.endswith('.cp2k.out'):
                from horton.io.cp2k import load_atom_cp2k
                result.update(load_atom_cp2k(filename, lf))
            elif filename.endswith('.cif'):
                from horton.io.cif import load_cif
                result.update(load_cif(filename, lf))
            else:
                raise ValueError('Unknown file format for reading: %s' % filename)

        # Apply changes in orbital order and sign conventions
        if 'permutation' in result:
            for key, value in result.iteritems():
                if isinstance(value, LinalgObject):
                    value.apply_basis_permutation(result['permutation'])
            del result['permutation']
        if 'signs' in result:
            for key, value in result.iteritems():
                if isinstance(value, LinalgObject):
                    value.apply_basis_signs(result['signs'])
            del result['signs']

        return cls(**result)

    def to_file(self, filename):
        '''Write molecule data to a file

           **Arguments:**

           filename
                The file to load the geometry from

           data
                A dictionary containing all the data. When some elements of the
                dictionary are not supported by the file format, they will be
                ignored. When for a given format, required elements are missing from
                the dictionary, an error is raised.

           This routine uses the extension or prefix of the filename to determine
           the file format. For each file format, a specialized dump_xxx function is
           called that does the real work.
        '''

        if isinstance(filename, h5.Group) or filename.endswith('.h5'):
            data = vars(self).copy()
            # get rid of leading underscores
            for key in data.keys():
                if key[0] == '_':
                    data[key[1:]] = data[key]
                    del data[key]
            from horton.io.internal import dump_h5
            if 'lf' in data:
                data.pop('lf')
            dump_h5(filename, data)
        elif filename.endswith('.xyz'):
            from horton.io.xyz import dump_xyz
            dump_xyz(filename, self)
        elif filename.endswith('.cube'):
            from horton.io.cube import dump_cube
            dump_cube(filename, self)
        elif filename.endswith('.cif'):
            from horton.io.cif import dump_cif
            dump_cif(filename, self)
        elif filename.endswith('.molden.input'):
            from horton.io.molden import dump_molden
            dump_molden(filename, self)
        elif os.path.basename(filename).startswith('POSCAR'):
            from horton.io.vasp import dump_poscar
            return dump_poscar(filename, self)
        else:
            raise ValueError('Unknown file format for writing: %s' % filename)

    def copy(self):
        '''Return a shallow copy'''
        kwargs = vars(self).copy()
        # get rid of leading underscores
        for key in kwargs.keys():
            if key[0] == '_':
                kwargs[key[1:]] = kwargs[key]
                del kwargs[key]
        return self.__class__(**kwargs)

    def get_dm_full(self):
        '''Return a spin-summed density matrix using availlable attributes'''
        if hasattr(self, 'dm_full'):
            return self.dm_full
        if hasattr(self, 'dm_full_mp2'):
            return self.dm_full_mp2
        elif hasattr(self, 'dm_full_mp3'):
            return self.dm_full_mp3
        elif hasattr(self, 'dm_full_ci'):
            return self.dm_full_ci
        elif hasattr(self, 'dm_full_cc'):
            return self.dm_full_cc
        elif hasattr(self, 'exp_alpha'):
            dm_full = self.lf.create_one_body()
            dm_full = self.exp_alpha.to_dm()
            if hasattr(self, 'exp_beta'):
                self.exp_beta.to_dm(dm_full, 1.0)
            else:
                dm_full.iscale(2)
            return dm_full
        elif hasattr(self, 'dm_full_scf'):
            return self.dm_full_scf

    def get_dm_spin(self):
        '''Return a spin-difference density matrix using availlable attributes'''
        if hasattr(self, 'dm_spin'):
            return self.dm_spin
        if hasattr(self, 'dm_spin_mp2'):
            return self.dm_spin_mp2
        elif hasattr(self, 'dm_spin_mp3'):
            return self.dm_spin_mp3
        elif hasattr(self, 'dm_spin_ci'):
            return self.dm_spin_ci
        elif hasattr(self, 'dm_spin_cc'):
            return self.dm_spin_cc
        elif hasattr(self, 'exp_alpha') and hasattr(self, 'exp_beta'):
            dm_spin = self.exp_alpha.to_dm()
            self.exp_beta.to_dm(dm_spin, -1.0)
            return dm_spin
        elif hasattr(self, 'dm_spin_scf'):
            return self.dm_spin_scf