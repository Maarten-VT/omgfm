from skbuild import setup

setup(
    name='cmark_gfm',
    version='0.1.1',
    description='Wrapper for cmark-gfm and some extra functionality to plug in logic before and after parsing Markdown',
    packages=['cmark_gfm'],
    install_requires=['scikit-build', 'cmake'],
    setup_requires=['scikit-build', 'cmake'],
    cmake_source_dir='omgfm/cmark_gfm_src', 
    cmake_install_dir='omgfm',
    zipsaf=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',],
    keywords='commonmark cmark_gfm',
    license='BSD',
    author='Maarten van Tilborg'   
)
