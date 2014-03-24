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
#pylint: skip-file


import numpy as np

from horton import *


def test_atom_si_uks():
    fn_out = context.get_fn('test/atom_si.cp2k.out')
    data = load_smart(fn_out)

    assert (data['numbers'] == [14]).all()
    assert (data['pseudo_numbers'] == [4]).all()
    assert (data['wfn'].exp_alpha.occupations == [1, 1, 1, 0]).all()
    assert (data['wfn'].exp_beta.occupations == [1, 0, 0, 0]).all()
    assert abs(data['wfn'].exp_alpha.energies - [-0.398761, -0.154896, -0.154896, -0.154896]).max() < 1e-4
    assert abs(data['wfn'].exp_beta.energies - [-0.334567, -0.092237, -0.092237, -0.092237]).max() < 1e-4
    assert abs(data['energy'] - -3.761587698067) < 1e-10
    assert (data['obasis'].shell_types == [0, 0, 1, 1, -2]).all()
    assert isinstance(data['wfn'], UnrestrictedWFN)
    assert data['wfn'].nel == 4

    olp = data['lf'].create_one_body()
    data['obasis'].compute_overlap(olp)
    ca = data['wfn'].exp_alpha.coeffs
    cb = data['wfn'].exp_beta.coeffs
    assert abs(np.diag(olp._array[:2,:2]) - np.array([0.42921199338707744, 0.32067871530183140])).max() < 1e-5
    assert abs(np.dot(ca.T, np.dot(olp._array, ca)) - np.identity(4)).max() < 1e-5
    assert abs(np.dot(cb.T, np.dot(olp._array, cb)) - np.identity(4)).max() < 1e-5



def test_atom_o_rks():
    fn_out = context.get_fn('test/atom_om2.cp2k.out')
    data = load_smart(fn_out)

    assert (data['numbers'] == [8]).all()
    assert (data['pseudo_numbers'] == [6]).all()
    assert (data['wfn'].exp_alpha.occupations == [1, 1, 1, 1]).all()
    assert abs(data['wfn'].exp_alpha.energies - [0.102709, 0.606458, 0.606458, 0.606458]).max() < 1e-4
    assert abs(data['energy'] - -15.464982778766) < 1e-10
    assert (data['obasis'].shell_types == [0, 0, 1, 1, -2]).all()
    assert isinstance(data['wfn'], RestrictedWFN)
    assert data['wfn'].nel == 8

    olp = data['lf'].create_one_body()
    data['obasis'].compute_overlap(olp)
    ca = data['wfn'].exp_alpha.coeffs
    assert abs(np.dot(ca.T, np.dot(olp._array, ca)) - np.identity(4)).max() < 1e-5
