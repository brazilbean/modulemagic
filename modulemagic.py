## modulemagic - IPython Notebook cell magic %%module
# Gordon Bean, April 2015

from IPython.core.magic import Magics, magics_class, cell_magic
import os, sys, importlib, argparse

## Functions for loading the extension
def load_ipython_extension(ipython):
    ipython.register_magics(ModuleMagics)
    
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
        # Parse the parameters
        parser = argparse.ArgumentParser('%%module cell magic')
        parser.add_argument('name')
        parser.add_argument('-p','--path', default=self.module_dir)
        args = parser.parse_args(line.split())
        
        name = args.name
        
        # Save to file
        os.makedirs(args.path, exist_ok=True)
        filename = os.path.join(args.path, name + '.py')
        with open(filename, 'w') as f:
            f.write(cell)

        # Import module
        if args.path not in sys.path:
            sys.path.insert(0, args.path)

        if name in sys.modules:
            # Always reload
            del sys.modules[name]

        module = importlib.import_module(name)
        
        if self.namespace:
            self.namespace[name] = module
        else:
            self.shell.push({name: module})

        return module

