# -*- coding: utf-8 -*-
# Horton is a Density Functional Theory program.
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
#pylint: skip-file

import numpy as np

import os
from horton import *
from horton.io.wfn import *
from horton.io.test.common import compute_mulliken_charges, compute_hf_energy


def test_load_wfn_low_he_s():
    fn_wfn = context.get_fn('test/he_s_orbital.wfn')
    numbers, coordinates, centers, type_assignment, exponents, mo_count, occ_num, mo_energy, coefficients = load_wfn_low(fn_wfn)
    assert numbers.shape == (1,)
    assert numbers == [2]
    assert coordinates.shape == (1,3)
    assert (coordinates == [0.00, 0.00, 0.00]).all()
    assert centers.shape == (4,)
    assert (centers == [0, 0, 0, 0]).all()
    assert type_assignment.shape == (4,)
    assert (type_assignment == [1, 1, 1, 1]).all()
    assert exponents.shape == (4,)
    assert (exponents == [0.3842163E+02, 0.5778030E+01, 0.1241774E+01, 0.2979640E+00]).all()
    assert mo_count.shape == (1,)
    assert mo_count == [1]
    assert occ_num.shape == (1,)
    assert occ_num == [2.0]
    assert mo_energy.shape == (1,)
    assert mo_energy == [-0.914127]
    assert coefficients.shape == (4, 1)
    assert (coefficients == np.array([0.26139500E+00, 0.41084277E+00, 0.39372947E+00, 0.14762025E+00]).reshape(4,1)).all()


def test_load_wfn_low_h2O():
    fn_wfn = context.get_fn('test/h2o_sto3g.wfn')
    numbers, coordinates, centers, type_assignment, exponents, mo_count, occ_num, mo_energy, coefficients = load_wfn_low(fn_wfn)
    assert numbers.shape == (3,)
    assert (numbers == np.array([8, 1, 1])).all()
    assert coordinates.shape == (3, 3)
    assert (coordinates[0] == [-4.44734101, 3.39697999, 0.00000000]).all()
    assert (coordinates[1] == [-2.58401495, 3.55136194, 0.00000000]).all()
    assert (coordinates[2] == [-4.92380519, 5.20496220, 0.00000000]).all()
    assert centers.shape == (21,)
    assert (centers[:15] == np.zeros(15, int)).all()
    assert (centers[15:] == np.array([1, 1, 1, 2, 2, 2])).all()
    assert type_assignment.shape == (21,)
    assert (type_assignment[:6] == np.ones(6)).all()
    assert (type_assignment[6:15] == np.array([2, 2, 2, 3, 3, 3, 4, 4, 4])).all()
    assert (type_assignment[15:] == np.ones(6)).all()
    assert exponents.shape == (21,)
    assert (exponents[ :3] == [0.1307093E+03, 0.2380887E+02, 0.6443608E+01]).all()
    assert (exponents[5:8] == [0.3803890E+00, 0.5033151E+01, 0.1169596E+01]).all()
    assert (exponents[13:16] == [0.1169596E+01, 0.3803890E+00, 0.3425251E+01]).all()
    assert exponents[-1] == 0.1688554E+00
    assert mo_count.shape == (5,)
    assert (mo_count == [1, 2, 3, 4, 5]).all()
    assert occ_num.shape == (5,)
    assert np.sum(occ_num) == 10.0
    assert (occ_num == [2.0, 2.0, 2.0, 2.0, 2.0]).all()
    assert mo_energy.shape == (5,)
    assert (mo_energy == np.sort(mo_energy)).all()
    assert (mo_energy[:3] == [-20.251576, -1.257549, -0.593857]).all()
    assert (mo_energy[3:] == [ -0.459729, -0.392617]).all()
    assert coefficients.shape == (21, 5)
    assert (coefficients[0] == [0.42273517E+01, -0.99395832E+00, 0.19183487E-11, 0.44235381E+00, -0.57941668E-14]).all()
    assert coefficients[ 6, 2] ==  0.83831599E+00
    assert coefficients[10, 3] ==  0.65034846E+00
    assert coefficients[17, 1] ==  0.12988055E-01
    assert coefficients[-1, 0] == -0.46610858E-03
    assert coefficients[-1,-1] == -0.33277355E-15


def test_setup_permutation1():
    assert (setup_permutation1(np.array([1, 1, 1])) == [0, 1, 2]).all()
    assert (setup_permutation1(np.array([1, 1, 2, 3, 4])) == [0, 1, 2, 3, 4]).all()
    assert (setup_permutation1(np.array([2, 3, 4])) == [0, 1, 2]).all()
    assert (setup_permutation1(np.array([2, 2, 3, 3, 4, 4])) == [0, 2, 4, 1, 3, 5]).all()
    assert (setup_permutation1(np.array([1, 1, 2, 2, 3, 3, 4, 4, 1])) == [0, 1, 2, 4, 6, 3, 5, 7, 8]).all()
    assert (setup_permutation1(np.array([1, 5, 6, 7, 8, 9, 10, 1])) == [0, 1, 2, 3, 4, 5, 6, 7]).all()
    assert (setup_permutation1(np.array([5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10])) == [0, 2, 4, 6, 8, 10, 1, 3, 5, 7, 9, 11]).all()
    assert (setup_permutation1(np.array([1, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9, 10])) == [0, 1, 3, 5, 2, 4, 6, 7, 8, 9, 10, 11, 12]).all()
    assert (setup_permutation1(np.array([11, 12, 13, 17, 14, 15, 18, 19, 16, 20])) == range(10)).all() # f orbitals
    assert (setup_permutation1(np.array([23, 29, 32, 27, 22, 28, 35, 34, 26, 31, 33, 30, 25, 24, 21])) == range(15)).all() # g orbitals
    assert (setup_permutation1(np.array([23, 29, 32, 27, 22, 28, 35, 34, 26, 31, 33, 30, 25, 24, 21])) == range(15)).all() # g orbitals
    assert (setup_permutation1(np.arange(36, 57)) == range(21)).all() # h orbitals
    assert (setup_permutation1(np.array([1, 1, 11, 12, 13, 17, 14, 15, 18, 19, 16, 20])) == range(12)).all()
    assert (setup_permutation1(np.array([2, 3, 4, 11, 12, 13, 17, 14, 15, 18, 19, 16, 20, 1, 1])) == range(15)).all()


def test_setup_permutation2():
    assert (setup_permutation2(np.array([1, 1, 1])) == [0, 1, 2]).all()
    assert (setup_permutation2(np.array([2, 2, 3, 3, 4, 4])) == [0, 2, 4, 1, 3, 5]).all()
    assert (setup_permutation2(np.array([1, 2, 3, 4, 1])) == [0, 1, 2, 3, 4]).all()
    assert (setup_permutation2(np.array([5, 6, 7, 8, 9, 10])) == [0, 3, 4, 1, 5, 2]).all()
    assert (setup_permutation2(np.repeat([5, 6, 7, 8, 9, 10], 2)) == [0, 6, 8, 2, 10, 4, 1, 7, 9, 3, 11, 5]).all()
    assert (setup_permutation2(np.arange(1, 11)) == [0, 1, 2, 3, 4, 7, 8, 5, 9, 6]).all()
    assert (setup_permutation2(np.array([1, 5, 6, 7, 8, 9, 10, 1])) == [0, 1, 4, 5, 2, 6, 3, 7]).all()
    assert (setup_permutation2(np.array([11, 12, 13, 17, 14, 15, 18, 19, 16, 20])) == [0, 4, 5, 3, 9, 6, 1, 8, 7, 2]).all()
    assert (setup_permutation2(np.array([1, 11, 12, 13, 17, 14, 15, 18, 19, 16, 20, 1])) == [0, 1, 5, 6, 4, 10, 7, 2, 9, 8, 3, 11]).all()
    assert (setup_permutation2(np.array([1, 11, 12, 13, 17, 14, 15, 18, 19, 16, 20, 2, 2, 3, 3, 4, 4])) == [0, 1, 5, 6, 4, 10, 7, 2, 9, 8, 3, 11, 13, 15, 12, 14, 16]).all()
    assert (setup_permutation2(np.array([1, 11, 12, 13, 17, 14, 15, 18, 19, 16, 20, 2, 3, 4, 5, 6, 7, 8, 9, 10])) == [0, 1, 5, 6, 4, 10, 7, 2, 9, 8, 3, 11, 12, 13, 14, 17, 18, 15, 19, 16]).all()
    assert (setup_permutation2(np.arange(36, 57)) == np.arange(21)[::-1]).all()
    assert (setup_permutation2(np.array([23, 29, 32, 27, 22, 28, 35, 34, 26, 31, 33, 30, 25, 24, 21])) == [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]).all()
    assert (setup_permutation2(np.arange(36, 57)) == range(21)[::-1]).all()


def test_setup_mask():
    assert (setup_mask(np.array([2, 3, 4])) == [True, False, False]).all()
    assert (setup_mask(np.array([1, 2, 3, 4, 1, 2, 3, 4])) == [True, True, False, False, True, True, False, False]).all()
    assert (setup_mask(np.array([5, 6, 7, 8, 9, 10])) == [True, False, False, False, False, False]).all()
    assert (setup_mask(np.array([2, 3, 4, 1, 5, 6, 7, 8, 9, 10])) == [True, False, False, True, True, False, False, False, False, False]).all()
    assert (setup_mask(np.arange(11, 21)) == [True, False, False, False, False, False, False, False, False, False]).all()
    assert (setup_mask(np.array([21, 24, 25])) == [True, False, False]).all()
    assert (setup_mask(np.array([11, 21, 36, 1])) == [True, True, True, True]).all()


def check_load_wfn(name):
    # system out of *.wfn file
    fn_wfn = context.get_fn('test/%s.wfn' % name)
    data1 = load_smart(fn_wfn)
    # system out of *.fchk file
    data2 = load_smart(context.get_fn('test/%s.fchk' % name))
    # Coordinates check:
    assert (abs(data1['coordinates'] - data2['coordinates']) < 1e-6).all()
    # Numbers check
    numbers1 = data1['numbers']
    numbers2 = data2['numbers']
    assert (numbers1 == numbers2).all()
    # Basis Set check:
    obasis1 = data1['obasis']
    obasis2 = data2['obasis']
    assert obasis1.nbasis == obasis2.nbasis
    assert (obasis1.shell_map == obasis2.shell_map).all()
    assert (obasis1.shell_types == obasis2.shell_types).all()
    assert (obasis1.nprims == obasis2.nprims).all()
    assert (abs(obasis1.alphas - obasis2.alphas) < 1.e-4).all()
    # Comparing MOs (*.wfn might not contain virtual orbitals):
    wfn1 = data1['wfn']
    wfn2 = data2['wfn']
    n_mo = wfn1.exp_alpha.nfn
    assert (abs(wfn1.exp_alpha.energies - wfn2.exp_alpha.energies[:n_mo]) < 1.e-5).all()
    assert (wfn1.exp_alpha.occupations == wfn2.exp_alpha.occupations[:n_mo]).all()
    assert (abs(wfn1.exp_alpha.coeffs   - wfn2.exp_alpha.coeffs[:,:n_mo]) < 1.e-7).all()
    # Check overlap
    lf1 = data1['lf']
    olp1 = lf1.create_one_body()
    obasis1.compute_overlap(olp1)
    lf2 = data2['lf']
    olp2 = lf2.create_one_body()
    obasis2.compute_overlap(olp2)
    assert (abs(olp1._array[:] - olp2._array[:]) < 1e-6).all()
    # Check energy
    energy1 = compute_hf_energy(data1)
    energy2 = compute_hf_energy(data2)
    assert abs(energy1 - energy2) < 1e-5
    # Check normalization
    wfn1.exp_alpha.check_normalization(olp1, 1e-5)
    # Check charges
    charges1 = compute_mulliken_charges(obasis1, lf1, numbers1, wfn1)
    charges2 = compute_mulliken_charges(obasis2, lf2, numbers2, wfn2)
    return wfn1, energy1, charges1


def test_load_wfn_he_s_virtual():
    wfn, energy, charges = check_load_wfn('he_s_virtual')
    assert isinstance(wfn, RestrictedWFN)
    assert abs(energy - (-2.855160426155)) < 1.e-6     #Compare to the energy printed in wfn file
    assert (abs(charges - [0.0]) < 1e-5).all()


def test_load_wfn_he_s():
    wfn, energy, charges = check_load_wfn('he_s_orbital')
    assert isinstance(wfn, RestrictedWFN)
    assert abs(energy - (-2.855160426155)) < 1.e-6     #Compare to the energy printed in wfn file
    assert (abs(charges - [0.0]) < 1e-5).all()


def test_load_wfn_he_sp():
    wfn, energy, charges = check_load_wfn('he_sp_orbital')
    assert isinstance(wfn, RestrictedWFN)
    assert abs(energy - (-2.859895424589)) < 1.e-6     #Compare to the energy printed in wfn file
    assert (abs(charges - [0.0]) < 1e-5).all()


def test_load_wfn_he_spd():
    wfn, energy, charges = check_load_wfn('he_spd_orbital')
    assert isinstance(wfn, RestrictedWFN)
    assert abs(energy - (-2.855319016184)) < 1.e-6     #Compare to the energy printed in wfn file
    assert (abs(charges - [0.0]) < 1e-5).all()


def test_load_wfn_he_spdf():
    wfn, energy, charges = check_load_wfn('he_spdf_orbital')
    assert isinstance(wfn, RestrictedWFN)
    assert abs(energy - (-1.100269433080)) < 1.e-6   #Compare to the energy printed in wfn file
    assert (abs(charges - [0.0]) < 1e-5).all()


def test_load_wfn_he_spdfgh():
    wfn, energy, charges = check_load_wfn('he_spdfgh_orbital')
    assert isinstance(wfn, RestrictedWFN)
    assert abs(energy - (-1.048675168346)) < 1.e-6   #Compare to the energy printed in wfn file
    assert (abs(charges - [0.0]) < 1e-5).all()


def test_load_wfn_he_spdfgh_virtual():
    wfn, energy, charges = check_load_wfn('he_spdfgh_virtual')
    assert isinstance(wfn, RestrictedWFN)
    assert abs(energy - (-1.048675168346)) < 1.e-6   #Compare to the energy printed in wfn file
    assert (abs(charges - [0.0]) < 1e-5).all()


def check_wfn(fn_wfn, restricted, nbasis, energy, charges):
    fn_wfn = context.get_fn(fn_wfn)
    data = load_smart(fn_wfn)
    numbers = data['numbers']
    coordinates = data['coordinates']
    wfn = data['wfn']
    obasis = data['obasis']
    lf = data['lf']
    assert obasis.nbasis == nbasis
    olp = lf.create_one_body()
    obasis.compute_overlap(olp)
    if restricted:
        assert isinstance(wfn, RestrictedWFN)
        wfn.exp_alpha.check_normalization(olp, 1e-5)
    else:
        assert isinstance(wfn, UnrestrictedWFN)
        wfn.exp_alpha.check_normalization(olp, 1e-5)
        wfn.exp_beta.check_normalization(olp, 1e-5)
    if energy is not None:
        myenergy = compute_hf_energy(data)
        assert abs(energy - myenergy) < 1e-5
    mycharges = compute_mulliken_charges(obasis, lf, numbers, wfn)
    assert (abs(charges - mycharges) < 1e-5).all()
    return obasis, wfn, lf, coordinates, numbers


def test_load_wfn_h2o_sto3g_decontracted():
    check_wfn(
        'test/h2o_sto3g_decontracted.wfn',
        True, 21, -75.162231674351,
        np.array([-0.546656, 0.273328, 0.273328]),
    )


def test_load_wfn_h2_ccpvqz_virtual():
    obasis, wfn, lf, coordinates, numbers = check_wfn(
        'test/h2_ccpvqz.wfn',
        True, 74, -1.133504568400,
        np.array([0.0, 0.0]),
    )
    assert (abs(obasis.alphas[:5] - [82.64000, 12.41000, 2.824000, 0.7977000, 0.2581000]) < 1.e-5).all()
    assert (wfn.exp_alpha.energies[:5] == [-0.596838, 0.144565, 0.209605, 0.460401, 0.460401]).all()
    assert (wfn.exp_alpha.energies[-5:] == [12.859067, 13.017471, 16.405834, 25.824716, 26.100443]).all()
    assert (wfn.exp_alpha.occupations[:5] == [1.0, 0.0, 0.0, 0.0, 0.0] ).all()
    assert abs(wfn.exp_alpha.occupations.sum() - 1.0) < 1.e-6


def test_load_wfn_h2o_sto3g():
    check_wfn(
        'test/h2o_sto3g.wfn',
        True, 21, -74.965901217080,
        np.array([-0.330532, 0.165266, 0.165266])
    )


def test_load_wfn_li_sp_virtual():
    obasis, wfn, lf, coordinates, numbers = check_wfn(
        'test/li_sp_virtual.wfn',
        False, 8, -3.712905542719,
        np.array([0.0, 0.0])
    )
    assert abs(wfn.exp_alpha.occupations.sum() - 2.0) < 1.e-6
    assert abs(wfn.exp_beta.occupations.sum()  - 1.0) < 1.e-6
    assert (wfn.exp_alpha.occupations == [1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).all()
    assert (wfn.exp_beta.occupations  == [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).all()
    assert (abs(wfn.exp_alpha.energies - [-0.087492, -0.080310, 0.158784, 0.158784, 1.078773, 1.090891, 1.090891, 49.643670]) < 1.e-6).all()
    assert (abs(wfn.exp_beta.energies  - [-0.079905, 0.176681, 0.176681, 0.212494, 1.096631, 1.096631, 1.122821, 49.643827]) < 1.e-6).all()
    assert wfn.exp_alpha.coeffs.shape == (8, 8)
    assert wfn.exp_beta.coeffs.shape  == (8, 8)


def test_load_wfn_li_sp():
    fn_wfn = context.get_fn('test/li_sp_orbital.wfn')
    data = load_smart(fn_wfn)
    wfn = data['wfn']
    assert isinstance(wfn, UnrestrictedWFN)
    assert wfn.exp_alpha.nfn == 2
    assert wfn.exp_beta.nfn == 1


def test_load_wfn_o2():
    obasis, wfn, lf, coordinates, numbers = check_wfn(
        'test/o2_uhf.wfn',
        False, 72, -149.664140769678,
        np.array([0.0, 0.0]),
    )
    assert wfn.exp_alpha.nfn == 9
    assert wfn.exp_beta.nfn == 7


def test_load_wfn_o2_virtual():
    obasis, wfn, lf, coordinates, numbers = check_wfn(
        'test/o2_uhf_virtual.wfn',
        False, 72, -149.664140769678,
        np.array([0.0, 0.0]),
    )
    assert abs(wfn.exp_alpha.occupations.sum() - 9.0) < 1.e-6
    assert abs(wfn.exp_beta.occupations.sum()  - 7.0) < 1.e-6
    assert wfn.exp_alpha.occupations.shape == (44,)
    assert wfn.exp_beta.occupations.shape  == (44,)
    assert (wfn.exp_alpha.occupations[:9] == np.ones(9)).all()
    assert (wfn.exp_beta.occupations[:7]  == np.ones(7)).all()
    assert (wfn.exp_alpha.occupations[9:] == np.zeros(35)).all()
    assert (wfn.exp_beta.occupations[7:]  == np.zeros(37)).all()
    assert wfn.exp_alpha.energies.shape == (44,)
    assert wfn.exp_beta.energies.shape  == (44,)
    assert wfn.exp_alpha.energies[0]  == -20.752000
    assert wfn.exp_alpha.energies[10] == 0.179578
    assert wfn.exp_alpha.energies[-1] ==  51.503193
    assert wfn.exp_beta.energies[0]  == -20.697027
    assert wfn.exp_beta.energies[15] ==  0.322590
    assert wfn.exp_beta.energies[-1] ==  51.535258
    assert wfn.exp_alpha.coeffs.shape == (72, 44)
    assert wfn.exp_beta.coeffs.shape  == (72, 44)


def test_load_wfn_lif_fci():
    obasis, wfn, lf, coordinates, numbers = check_wfn(
        'test/lif_fci.wfn',
        True, 44, None,
        np.array([-0.645282, 0.645282]),
    )
    assert wfn.exp_alpha.occupations.shape == (18,)
    assert abs(wfn.exp_alpha.occupations.sum() - 6.0) < 1.e-6
    assert wfn.exp_alpha.occupations[0] == 2.00000000/2
    assert wfn.exp_alpha.occupations[10] == 0.00128021/2
    assert wfn.exp_alpha.occupations[-1] == 0.00000054/2
    assert wfn.exp_alpha.energies.shape == (18,)
    assert wfn.exp_alpha.energies[0] == -26.09321253
    assert wfn.exp_alpha.energies[15] == 1.70096290
    assert wfn.exp_alpha.energies[-1] == 2.17434072
    assert wfn.exp_alpha.coeffs.shape == (44, 18)
    kin = lf.create_one_body()
    obasis.compute_kinetic(kin)
    expected_kin = 106.9326884815  #FCI kinetic energy
    expected_nn = 9.1130265227
    assert (kin.expectation_value(wfn.dm_full) - expected_kin) < 1.e-6
    assert (compute_nucnuc(coordinates, numbers) - expected_nn) < 1.e-6
    points = np.array([[0.0, 0.0,-0.17008], [0.0, 0.0, 0.0], [0.0, 0.0, 0.03779]])
    density = np.zeros(3)
    obasis.compute_grid_density_dm(wfn.dm_full, points, density)
    assert (abs(density - [0.492787, 0.784545, 0.867723]) < 1.e-4).all()


def test_load_wfn_lih_cation_fci():
    obasis, wfn, lf, coordinates, numbers = check_wfn(
        'test/lih_cation_fci.wfn',
        True, 26, None,
        np.array([0.913206, 0.086794]),
    )
    assert (numbers == [3, 1]).all()
    expected_kin = 7.7989675958  #FCI kinetic energy
    expected_nn = 0.9766607347
    kin = lf.create_one_body()
    obasis.compute_kinetic(kin)
    assert (kin.expectation_value(wfn.dm_full) - expected_kin) < 1.e-6
    assert (compute_nucnuc(coordinates, numbers) - expected_nn) < 1.e-6
    assert wfn.exp_alpha.occupations.shape == (11,)
    assert abs(wfn.exp_alpha.occupations.sum() - 1.5) < 1.e-6
