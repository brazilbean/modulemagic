## beans.magics
# Gordon Bean, April 2015

# To use these magics, you must register them with IPython
# e.g:
# from beans.magics import ModuleMagics
# ip = get_ipython()
# ip.register_magics(ModuleMagics)

from IPython.core.magic import Magics, magics_class, cell_magic
import os, sys, importlib

@magics_class
class ModuleMagics(Magics):
    '''Magics for creating modules in IPython.'''
    
    def __init__(self, shell=None, namespace=None):
        if shell is None:
            shell = get_ipython()
            
        super(ModuleMagics, self).__init__(shell)
        
        self.namespace = namespace
        
        # Get the kernel id
        self.kernelID = os.path.basename(shell.kernel.config['IPKernelApp']['connection_file'])[:-5]
        
        # Create kernel-specific tmp-module directory
        self.module_dir = os.path.join('/tmp/.tmp-modules', self.kernelID)
        os.makedirs(self.module_dir, exist_ok=True)
    
    def __del__(self):
        # Remove module_dir from file system and sys.path
        # I'm not sure this works - evidence so far says no...
        tmpfiles = os.listdir(self.module_dir)
        for file in tmpfiles:
            os.remove(os.path.join(self.module_dir, file))
            
        os.rmdir(self.module_dir)
        
        sys.path.remove(self.module_dir)
    
    @cell_magic
    def module(self, line, cell):
        '''Import the cell as a module.'''
        # Parse module name
        tokens = line.split()
        name = tokens[0]

        # Save to file
        filename = os.path.join(self.module_dir, name + '.py')
        with open(filename, 'w') as f:
            f.write(cell)

        # Import module
        if self.module_dir not in sys.path:
            sys.path.insert(0, self.module_dir)

        if name in sys.modules:
            # Always reload
            del sys.modules[name]

        module = importlib.import_module(name)
        
        if self.namespace:
            self.namespace[name] = module
        else:
            self.shell.push({name: module})

        return module

