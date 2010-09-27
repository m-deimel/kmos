#!/usr/bin/python
"""Generical kMC steering script for binary modules created kmos"""

import kmc
from ConfigParser import ConfigParser
from numpy import array

CONFIG = """[standard]
system_size = 10 10
system_name = foobar
default_species = empty
"""

class KMC_Run():
    def __init__(self):
        self.nr_of_proc = kmc.proclist.nr_of_proc
        # Write config file first
        config_filename = 'kmc.ini'
        config_file = open(config_filename, 'w')
        config_file.write(CONFIG)
        config_file.close()

        # Read config file
        config = ConfigParser()
        config.read(config_filename)
        size = config.get('standard', 'system_size')
        size = [ int(x) for x in size.split() ]
        name = config.get('standard', 'system_name')
        kmc.proclist.init(size, name)

        default_species = config.get('standard', 'default_species')

        # initialize name arrays
        self.process_names = []
        self.rate_expressions = []
        for i in range(kmc.proclist.nr_of_proc):
            self.rate_expressions.append(get_rate_expression(i+1))
            self.process_names.append(get_process_name(i+1))
        self.species_names = []
        for i in range(kmc.lattice.nr_of_species):
            self.species_names.append(get_species_name(i+1))
        self.lattice_names = []
        for i in range(kmc.lattice.nr_of_lattices):
            self.lattice_names.append(get_lattice_name(i+1))
        self.lattice_name = self.lattice_names[0]
        self.site_names = []
        for i in range(kmc.lattice.nr_of_sites):
            self.site_names.append(get_site_name(i+1))


        self.base = eval('kmc.lattice.lookup_nr2%s' % self.lattice_name)

        for y in range(size[1]):
            for x in range(size[0]):
                self.fill_unit_cell(x, y, default_species)

        for x in range(size[0]):
            for y in range(size[1]):
                self.touchup_unit_cell(x, y)


        self.set_rates()



    def run(self):
        for i in xrange(int(1.e6)):
            kmc.proclist.do_kmc_step()

    def set_rates(self):
        """For testing purpose we set all rates to a constant
        until formula and parameter support is implemented
        """
        for proc_nr in range(kmc.proclist.nr_of_proc):
            kmc.base.set_rate(proc_nr+1, 50.0)

    def fill_unit_cell(self, x, y, species):
        species = eval('kmc.lattice.%s' % species)
        base = eval('kmc.lattice.lookup_nr2%s' % self.lattice_name)
        A = kmc.lattice.lattice_matrix
        for site in base:
            current_site = x*A[0] + y*A[1] + site
            old_species = eval('kmc.lattice.%s_get_species' % self.lattice_name)(current_site)
            eval('kmc.lattice.%s_replace_species' % self.lattice_name)(current_site, old_species, species)

    def touchup_unit_cell(self, x, y):
        A = kmc.lattice.lattice_matrix
        for i, site in enumerate(self.site_names):
            current_site = x*A[0] + y*A[1] + self.base[i]
            touchup = eval('kmc.proclist.touchup_%s_site' % site)
            touchup(current_site)


    def get_occupation(self):
        occupation = {}
        for species_name in self.species_names:
            occupation[species_name] = 0
        for y in range(size[1]):
            for x in range(size[0]):
                pass

def get_rate_expression(process_nr):
    """Workaround function for f2py's inability to return character arrays, better known as strings.
    """
    rate_expr = ''
    i = 1
    while True:
        new_char = kmc.proclist.get_rate_char(process_nr, i)
        if new_char == ' ':
            break
        rate_expr += new_char
        i += 1
    return rate_expr

def get_process_name(process_nr):
    """Workaround function for f2py's inability to return character arrays, better known as strings.
    """
    process_name = ''
    i = 1
    while True:
        new_char = kmc.proclist.get_process_char(process_nr, i)
        if new_char == ' ':
            break
        process_name += new_char
        i += 1
    return process_name.lower()

def get_species_name(species_nr):
    """Workaround function for f2py's inability to return character arrays, better known as strings.
    """
    species_name = ''
    i = 1
    while True:
        new_char= kmc.lattice.get_species_char(species_nr, i)
        if new_char == ' ':
            break
        species_name += new_char
        i += 1
    return species_name.lower()

def get_lattice_name(lattice_nr):
    """Workaround function for f2py's inability to return character arrays, better known as strings.
    """
    lattice_name = ''
    i = 1
    while True:
        new_char= kmc.lattice.get_lattice_char(lattice_nr, i)
        if new_char == ' ':
            break
        lattice_name += new_char
        i += 1
    return lattice_name.lower()


def get_site_name(site_nr):
    """Workaround function for f2py's inability to return character arrays, better known as strings.
    """
    site_name = ''
    i = 1
    while True:
        new_char= kmc.lattice.get_site_char(site_nr, i)
        if new_char == ' ':
            break
        site_name += new_char
        i += 1
    return site_name.lower()

if __name__ == '__main__':
    kmc_run = KMC_Run()
    kmc_run.set_rates()
    kmc_run.run()
