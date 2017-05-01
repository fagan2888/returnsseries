#
#    Copyright (C) 2017 Brooksbridge Capital LLP
#
#    This file is part of returnsseries.
#    
#    returnsseries is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    returnsseries is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with returnsseries.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

setup(name='returnsseries',
      version='0.1.0',
      author='Brooksbridge Capital LLP',
      author_email='thomas.smith@brooksbridge.com',
      license='GPL',
      keywords=['finance', 'returns', 'pandas', 'series'],
      url='XXXX',
      
      packages=['returnsseries',],
      package_data={'returnsseries':['data/*']},
      install_requires=['numpy',
                        'pandas', 
                        'matplotlib',
                        ],
      )
