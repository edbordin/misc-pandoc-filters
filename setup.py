from setuptools import setup

setup(name='misc_pandoc_filters',
      version='0.1',
      description='Misc. pandoc filters',
      url='http://github.com/edbordin/misc-pandoc-filters',
      author='Edward Bordin',
      author_email='edbordin@gmail.com',
      license='None',
      packages=['misc_pandoc_filters'],
      install_requires=['panflute','pandocfilters'],
      zip_safe=False,
      entry_points = {
        'console_scripts': ['pandoc-acro=misc_pandoc_filters.acro:main',
                            'pandoc-docx=misc_pandoc_filters.docx_extensions:main',
                            'pandoc-svg=misc_pandoc_filters.pandoc_svg:main'],
    })