# TAU Setup for NX
- download and unzip tau from [here](https://www.cs.uoregon.edu/research/tau/home.php) and etc from [here](http://tau.uoregon.edu/ext.tgz)
- untar TAU
- untar etc within the new TAU directory
- within the top level of the TAU directory, configure the tool to your machine
    - ./configure -bfd=download -dwarf=download -unwind=download -iowrapper -pythoninc=<dir> -pythonlib=<dir>
    - pythoninc is the python include directory where Python.h is stored
        - By default Python.h is not installed, do sudo apt-get install python3-dev
        - It can likely be found in /usr/include/python3.x
    - pythonlib is where the python shared object file(.so) is located
        - Can be found in /usr/lib/aarch64-linux-gnu/
            - if you have multiple versions of python installed, TAU will use the first one it finds, so if you want to use the 3.x.so file I recommend making a copy in a separate directory
    - Compilers
        - If TAU complains about compilers add -c++=g++ and -cc=gcc to the configure command
- Once configure completes, add the TAU/arch/bin directoy to your path
    - ./configure outputs the exact filepath you need to add to path
    - ex: export PATH="/home/nvidia/Documents/tau-2.30.1/arm64_linux/bin:$PATH"
- Run Make Install
- Add /TAU DIR/ARCH/lib/bindings-python to the PYTHONPATH
    ex: export PYTHONPATH=/home/nvidia/Documents/tau-2.30.1/arm64_linux/lib/bindings-python
- You can now do automatic and manual TAU instrumentation for profiling
    - Auto
        - import tau
        - tau.run("main_function()")
    - Manual
        - import pytau
        - see TAU reference
- After the program runs
    - Auto
        - outputs a profile.0.0.0 file
        - run pprof to view
    - Manual
        - outputs a profile.1.0.0 file
        - rename to profile.0.0.0 and run pprof

# Wrapper
- run python3 wrapper.py filename.py arg1 arg2 ...
    - Auto instruments filename.py