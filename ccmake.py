#
# TODO:
#     * Add function to find depdend files from sources( *.c, *.cpp )
#



import os
import re, subprocess


import sys
def print_error(string):
    if sys.platform.startswith( 'win' ):
        import win32console
        font_color = win32console.FOREGROUND_INTENSITY|win32console.FOREGROUND_RED
        console = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
        old_color = console.GetConsoleScreenBufferInfo()['Attributes']
        console.SetConsoleTextAttribute(font_color)
        print( string )
        console.SetConsoleTextAttribute(old_color)
    else:
        print( string )

def print_warning(string):
    if sys.platform.startswith( 'win' ):
        import win32console
	font_color = win32console.FOREGROUND_INTENSITY|win32console.FOREGROUND_RED|win32console.FOREGROUND_GREEN
	console = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
	old_color = console.GetConsoleScreenBufferInfo()['Attributes']
	console.SetConsoleTextAttribute(font_color)
	print( string )
	console.SetConsoleTextAttribute(old_color)
    else:
        print( string )

def print_ok(string):
    if sys.platform.startswith( 'win' ):
        import win32console
        font_color = win32console.FOREGROUND_INTENSITY|win32console.FOREGROUND_GREEN
        console = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
        old_color = console.GetConsoleScreenBufferInfo()['Attributes']
        console.SetConsoleTextAttribute(font_color)
        print( string )
        console.SetConsoleTextAttribute(old_color)
    else:
        print( string )

def print_info(string):
	# font_color = win32console.FOREGROUND_INTENSITY|win32console.FOREGROUND_GREEN|win32console.FOREGROUND_RED|win32console.FOREGROUND_BLUE
	# console = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
	# old_color = console.GetConsoleScreenBufferInfo()['Attributes']
	# console.SetConsoleTextAttribute(font_color)
	print( string )
	# console.SetConsoleTextAttribute(old_color)

##############################################################################
def test_cpp3():

    # $(source) $(target) are placeholder variables, they won't be evaluated even eval_var == True.
    ccmake_set_placeholder_variable( "source" )
    ccmake_set_placeholder_variable( "target" )

    #ccmake_set_variable( name, variable_string, eval_var = True )
    ccmake_set_variable( "INCLUDE", "./code/include;./code;./system/include" )
    ccmake_set_variable( "CXX", "./tool/cl.exe" )
    ccmake_set_variable( "CFLAGS_DEBUG", "/nologo /Zi /W4 /WX /GR- /D_CRT_SECURE_NO_WARNINGS /DDEBUG" )
    ccmake_set_variable( "CFLAGS_RELEASE", "/nologo /Zi /W4 /WX /GR- /D_CRT_SECURE_NO_WARNINGS /DNDEBUG" )

    ccmake_set_variable( "LDFLAGS", "/DEBUG /libpath:$(BUILDDIR) /LTCG /OPT:REF /OPT:ICF" )

    # ccmake_set_command( name, tool, paramters )
    ccmake_set_command( "CPP_COMPILE_DEBUG",   "$(CXX)", "$(CFLAGS_DEBUG) -c $(source) /Fo$(target)"         )
    ccmake_set_command( "CPP_COMPILE_RELEASE", "$(CXX)", "$(CFLAGS_RELEASE) -c $(source) /Fo$(target)"       )
    ccmake_set_command( "LINK",                "$(CXX)", "$(source) /nologo /link $(LDFLAGS) /out:$(target)" )

    maked = create_make( "debug" )
    # add_build( command_name, $(target), $(source), extra_dependencies ):
    # full dependencies = [source, extra_dependencies ]
    maked.add_build( "CPP_COMPILE_DEBUG", "./debug/a.obj",    "./code/a.cpp"    )
    maked.add_build( "CPP_COMPILE_DEBUG", "./debug/b.obj",    "./code/b.cpp"    )
    maked.add_build( "CPP_COMPILE_DEBUG", "./debug/c.obj",    "./code/c.cpp"    )
    maked.add_build( "CPP_COMPILE_DEBUG", "./debug/main.obj", "./code/main.cpp" )
    maked.add_build( "LINK", "./debug/main.exe", [
        "./debug/a.obj",
        "./debug/b.obj",
        "./debug/c.obj",
        "./debug/main.obj" ]
        )

    # Create target(dependency) tree in run method.
    # Then execute build from leaves to root.
    maked.run_build( "./debug/main.exe" )

    maked.set_default_build( "./debug/main.exe" )
    maked.run() # build from default.

    make = create_make( "release" )
    make.add_build( "CPP_COMPILE_RELEASE", "./release/a.obj",    "./code/a.cpp"    )
    make.add_build( "CPP_COMPILE_RELEASE", "./release/b.obj",    "./code/b.cpp"    )
    make.add_build( "CPP_COMPILE_RELEASE", "./release/c.obj",    "./code/c.cpp"    )
    make.add_build( "CPP_COMPILE_RELEASE", "./release/main.obj", "./code/main.cpp" )
    make.add_build( "LINK", "./release/main.exe", [
        "./release/a.obj",
        "./release/b.obj",
        "./release/c.obj",
        "./release/main.obj" ]
        )

    make.run_build( "./release/main.exe" )

    make.set_default_build( "./release/main.exe" )
    make.run() # build from default.

#if __name__ == '__main__':
#    test_path()


# Make sure dir_path exists.
def ensure_dir_path( dir_path ):
    if not os.path.exists( dir_path ):
        os.makedirs( dir_path )

    return os.path.exists( dir_path )

# Find file with name in dirs
def find_file_in_dirs( name, dirs ):
    for d in dirs:
        path = d + '/' + name
        path = os.path.normpath( path )
        if os.path.exists( path ):
            return path
    return ''

# Check if string contains var.
def has_var( string, skipped_vars ):
    # Clear skipped vars in string.
    for name in skipped_vars:
        string = string.replace( '$(' + name + ')', '' )
    patern = '\$\((.+?)\)'
    m = re.search( patern, string )
    return m != None

def ccmake_touch_file( in_path ):
    with open( in_path, 'a' ):
        os.utime( in_path, None )

def ccmake_find_include_files( code_path, dirs = [] ):
    result = []
    code_f = open( code_path, 'r' )
    for line in code_f:
        idx0 = line.find( '#' )
        if idx0 < 0: continue
        idx1 = line.find( 'include', idx0 )
        if idx1 < 0: continue
        idx2 = line.find( '"', idx1 )
        if idx2 < 0: continue
        idx3 = line.find( '"', idx2 + 1 )
        if idx3 < 0: continue

        include_name = line[idx2 + 1 : idx3].strip()

        # Added dir of code_path into dirs
        dirs.append( os.path.dirname( code_path ) )

        path = find_file_in_dirs( include_name, dirs )
        result.append( path )

    # Unique result.
    if len( result ) > 0:
        result = list( set ( result ) )

        # find include file recursively.
        for path in result:
            subs = ccmake_find_include_files( path )
            if len( subs ) > 0: result += subs

    return result


def ccmake_find_files( dir_path, name_pattern ):
    file_list = []
    for root, dirs, names in os.walk( dir_path ):
        for name in names:
            if re.match( name_pattern, name ):
                path = root + '/' + name
                file_list.append( os.path.normpath( path ) )
    return file_list

def ccmake_find_files_with_exts( dir_path, ext_list ):
    file_list = []
    for e in ext_list:
        file_list += ccmake_find_files( dir_path, '.+[.]' + e )
    return file_list

def ccmake_find_c_files( dir_path ):
    return ccmake_find_files_with_exts( dir_path, ['c'] )

def ccmake_find_cpp_files( dir_path ):
    return ccmake_find_files_with_exts( dir_path, ['cpp', 'cxx', 'cc'] )

def ccmake_create_builds_from_dir( cmd_obj, in_dir, in_ext, out_dir, out_ext ):
    in_list = ccmake_find_files_with_exts( dir_path, [ in_ext ] )
    out_list = []
    for n in in_list:
        rel_path = os.path.relpath( n, dir_path )
        name, ext = os.path.splitext( os.path.basename( n ) )
        out_path = out_dir + '/' + os.path.dirname( rel_path ) + name +'.' + out_ext
        out_path = os.path.normpath( out_path )

        out_list.append( out_path )

    



class Cmd( object ):
    def __init__( self, name, path, args, config_obj ):
        self.name   = name
        self.path   = path
        self.args   = args
        self.config = config_obj

    def always_run( self ):
        if self.config:
            if self.config.get_var( 'CCMAKE_ALWAYS_BUILD' ) == 'YES':
                return True
        return False

    def get_depend_file_list( self ):
        r = []
        full_path = self.get_full_path()
        if len( full_path ) > 0: 
            r.append( full_path )

        return r

    def get_full_path( self ):
        full_path = os.path.abspath( self.path )
        if os.path.exists( full_path ):
            return full_path
       
        # Needs to find the full path from PATH variable.
        if self.config:
            full_path = self.config.find_file_in_var( 'PATH', self.path )
            if len( full_path ) > 0: return full_path

        # Cannot find the cmd file.
        print_error( "Cannot find cmd file " + self.path )
        return ''

    def get_args_depend_path( self ):

        out_root = self.config.get_var( 'CCMAKE_OUT' )
        if len( out_root ) == 0: return ''

        # Set the cmd depdend file dir.
        cmd_base_dir = os.path.normpath( out_root + '/cmds/deps/' )
        if not ensure_dir_path( cmd_base_dir ): return ''

        # Name of args depend file.
        args_dep_file = cmd_base_dir + '/' + os.path.basename( self.path ) + '.d'

        return args_dep_file

    def get_dep_content_list( self ):
        dep_content_list = []
        dep_content_list.append( self.get_full_path() )
        dep_content_list.append( self.args )
        return dep_content_list

    def create_args_depend_file( self, dep_file_path ):
        #        # create args depend file.
        #        args_dep_file = self.get_args_depend_path()

        #        if len( args_dep_file ) == 0: return False

        dep_content = self.get_full_path() + '\n' + self.args + '\n'

        if os.path.exists( dep_file_path ):
            # dep file is already existed, check if the make file modified,
            # if so, re-create the dep file.
            # Maybe this is a little bit complicated.

            # Right now I just read the content in dep file, if it is same as
            # args, then do nothing, if not same, re-create the dep file.

            in_f = open( dep_file_path, 'r' )
            if in_f:
                old_content = in_f.read()
                in_f.close()
            if old_content != dep_content:
                # delete this old dep file.
                os.remove( dep_file_path )

        # Check the dep file again, create if it doesn't exist.
        if not os.path.exists( dep_file_path ):
            out_f = open( dep_file_path, 'w' )
            if out_f:
                out_f.write( dep_content )
                out_f.close()

        if os.path.exists( dep_file_path ):
            return True
        return False

    def execute( self, targets, sources ):
        targets_string = ' '.join( targets )
        sources_string = ' '.join( sources )

        args = self.args
        args = args.replace( '$(source)', sources_string )
        args = args.replace( '$(target)', targets_string )
        args = args.replace( '$(sources)', sources_string )
        args = args.replace( '$(targets)', targets_string )

        exe = self.get_full_path()

        cmd = '"' + exe + '" ' + args
        print_info( cmd )
        pipe = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        out_str, err_str = pipe.communicate()
        for line in out_str.splitlines():
            if line.find( ' error ' ) != -1:
                print_error( line )
            elif line.find( ' warning ' ) != -1:
                print_warning( line )
            else:
                print_info( line )
        print_error( err_str )


class Depend( object ):
    def __init__( self, name_pattern, dep_function ):
        self.name_pattern = name_pattern
        self.dep_function = dep_function
    
    def match( self, name ):
        if re.match( self.name_pattern, name ): return True
        return False


class Config( object ):
    def __init__( self ):
        self.vars = {}
        self.cmds = {}
        self.placeholder_vars = [ "sources", "source", "target", "targets" ]
        self.missed_vars = []
        self.deps = []

        # Add preset Depend objects
        c_cpp_exts = [ 'c', 'cpp', 'cxx', 'cc', 'h', 'hpp' ]
        for ext in c_cpp_exts:
            dep_obj = Depend( '.+[.]' + ext, ccmake_find_include_files )
            self.deps.append( dep_obj )

    def get_dep_function( self, in_path ):
        name = os.path.basename( in_path )
        for d in self.deps:
            if d.match( name ):
                return d.dep_function
        return None

    def eval_var( self, var_value ):
        # Find vars in var_value string.
        patern = '\$\((.+?)\)'
        for m in re.finditer( patern, var_value ):
            #print_info( '        ' + m.group(1) )
            v_name = m.group(1)

            # Skip placeholder vars.
            if v_name in self.placeholder_vars: continue

            # Skip missed vars.
            if v_name in self.missed_vars: continue

            v_val = self.get_var( v_name )
            if v_val == '':
                print_error( "Cannot find var " + v_name + " for " + var_value )

                # Added v_name into missed_vars
                self.missed_vars.append( v_name )
            else:
                var_value = var_value.replace( m.group(0), v_val )

        # Create skipped var list.
        skipped_vars = self.placeholder_vars + self.missed_vars

        # Check if there still has var in var_value ( exclude skipped_vars ),
        # if so, evaluate it recursively.
        if has_var( var_value, skipped_vars ):
            print_info( '    has var' + var_value )
            var_value = self.eval_var( var_value )

        return var_value
            
    def set_var( self, var_name, var_value ):
        var_value = self.eval_var( var_value )
        self.vars[ var_name ] = var_value

    def get_var( self, var_name ):
        if var_name not in self.vars:
            # Check if it is in sytem environ
            if var_name in os.environ:
                return os.environ[ var_name ]
            else:
                return ''
        return self.vars[ var_name ]

    def set_cmd( self, cmd_name, cmd_path, cmd_args ):
        # Evaluate the var in path and args first.
        cmd_path = self.eval_var( cmd_path )
        cmd_args = self.eval_var( cmd_args )

        # create Cmd object.
        self.cmds[ cmd_name ] = Cmd( cmd_name, cmd_path, cmd_args, self )

    def has_cmd( self, cmd_name ):
        if cmd_name in self.cmds:
            return True
        return False

    def find_cmd( self, cmd_name ):
        if cmd_name in self.cmds:
            return self.cmds[ cmd_name ]
        return None

    def find_file_in_var( self, var_name, file_name ):
        var_value = self.get_var( var_name )
        dirs = var_value.split(';')
        for d in dirs:
            full_path = d + '/' + file_name
            full_path = os.path.normpath( full_path )
            if os.path.exists( full_path ):
                return full_path
        return ''

    def evaluate( self ):
        out_root = self.get_var( 'CCMAKE_OUT' )
        if len( out_root ) > 0: 

            # Create CCMAKE_OUT if it doesn't exist.
            if not os.path.exists( out_root ): os.makedirs( out_root )

            # Check the create result.
            if not os.path.exists( out_root ):
                print_error( "Failed create CCMAKE_OUT: " + out_root )

        #        # evaluate all $(var) in config.vars, report vars which not defined.
        #        for var_name in self.vars:
        #            var_value = self.vars[ var_name ]
        #            var_value = self.eval_var( var_value )
        #            self.vars[ var_name ] = var_value

class Build( object ):
    def __init__( self, cmd_obj, inputs, outputs, extra_deps ):
        self.cmd = cmd_obj
        if isinstance( inputs, list ):
            self.sources  = inputs
        else:
            self.sources = [ inputs ]

        if isinstance( outputs, list ):
            self.targets = outputs
        else:
            self.targets = [ outputs ]

        if isinstance( extra_deps, list ):
            self.extra_deps = extra_deps
        else:
            self.extra_deps = [ extra_deps ]


    def get_depend_file_list( self ):
        dep_list = self.cmd.get_depend_file_list()
        dep_list += [ t + '.d' for t in self.targets ]
        dep_list += self.sources
        dep_list += self.extra_deps
        return dep_list

    def get_dep_content_list( self ):
        dep_content_list = self.cmd.get_dep_content_list()
        dep_content_list += self.sources
        dep_content_list += self.extra_deps
        return dep_content_list

    def create_make_target( self ):
        return MakeTarget( self, self.targets )

    def ensure_dependencies( self ):
        # Check and create target depend files
        for t in self.targets:
            self.create_depdend_file( t + '.d' )


    def create_depdend_file( self, dep_file_path ):
        dep_content = ''
        dep_content_list = self.get_dep_content_list()
        for src in dep_content_list:
            dep_content += src + '\n'

        if os.path.exists( dep_file_path ):

            in_f = open( dep_file_path, 'r' )
            if in_f:
                old_content = in_f.read()
                in_f.close()
            if old_content != dep_content:
                # delete this old dep file.
                os.remove( dep_file_path )

        # Check the dep file again, create if it doesn't exist.
        if not os.path.exists( dep_file_path ):
            out_f = open( dep_file_path, 'w' )
            if out_f:
                out_f.write( dep_content )
                out_f.close()

        if os.path.exists( dep_file_path ):
            return True
        return False
        


    # Return True if need to rebuild.
    def check_dependencies( self ):
        # Check if always run build
        if self.cmd.always_run(): return True

        # Get the oldest target date
        target_time = -1
        for t in self.targets:
            if os.path.exists( t ):
                file_change_time = os.path.getmtime( t )
                if target_time < 0 or file_change_time < target_time:
                    target_time = file_change_time

        # get the latest source date
        source_time = 0
        dep_list = self.get_depend_file_list()
        for d in dep_list:
            if os.path.exists( d ):
                file_change_time = os.path.getmtime( d )
                if file_change_time > source_time:
                    source_time = file_change_time

        # compare source date and target date.
        if source_time > target_time:
            # Need to rebuild
            return True
        return False
        
    def execute( self ):
        self.ensure_dependencies()

        if self.check_dependencies():
            self.cmd.execute( self.targets, self.sources )

class MakeTarget( object ):
    def __init__( self, build, objs ):
        self.build    = build
        self.objects  = objs
        self.children = []
        

class Make( object ):
    def __init__( self, name, cfg ):
        self.name   = name
        self.config = cfg 
        self.builds = []

    def has_cmd( self, cmd_name ):
        if self.config:
            return self.config.has_cmd( cmd_name )
        return False

    def find_cmd( self, cmd_name ):
        if self.config:
            return self.config.find_cmd( cmd_name )
        return None

    def get_extra_dep_list( self, in_path ):
        if not self.config: return []

        dep_function = self.config.get_dep_function( in_path )
        if not dep_function: return []

        return dep_function( in_path )

    def add_build( self, cmd_name, out_path, in_path, extra_dep_list=[] ):
        #print_info( "add build " + cmd_name )
        cmd_obj = self.find_cmd( cmd_name )
        if cmd_obj:
            self.builds.append( Build( cmd_obj, in_path, out_path, extra_dep_list ) )
        else:
            print_error( "Cannot find cmd: " + cmd_name )

    def add_build_object( self, build_obj ):
        if not isinstance( build_obj, Build ):
            print_error( "Input is not a instance of Build!" )
            return
        self.builds.append( build_obj )

    def add_builds_from_dir( self, cmd_name, out_dir, out_ext, in_dir, in_ext ):

        build_list = []

        cmd_obj = self.find_cmd( cmd_name )
        if not cmd_obj:
            print_error( "Cannot find cmd: " + cmd_name )
            return

        in_list = ccmake_find_files_with_exts( in_dir, [ in_ext ] )

        for in_path in in_list:
            rel_path = os.path.relpath( in_path, in_dir )
            name, ext = os.path.splitext( os.path.basename( in_path ) )
            out_path = out_dir + '/' + os.path.dirname( rel_path ) + name +'.' + out_ext
            out_path = os.path.normpath( out_path )
            extra_dep_list = self.get_extra_dep_list( in_path )
            build_obj = Build( cmd_obj, in_path, out_path, extra_dep_list )
            self.add_build_object( build_obj )

            build_list.append( build_obj )

        return build_list

    def find_build_with_target( self, target_name ):
        for b in self.builds:
            for t in b.targets:
                # Used abspath to find target, so it won't miss target if relpath in targets.
                if os.path.abspath( t ) == os.path.abspath( target_name ):
                    return b
        return None

    def create_target_recursively( self, start_target_name ):
        target_build = self.find_build_with_target( start_target_name )
        if target_build:
            # Gothrough every source in target_build,
            # check if it is a target in other build.

            make_target = target_build.create_make_target()
            for s in target_build.sources:
                child_target = self.create_target_recursively( s )
                if child_target != None:
                    make_target.children.append( child_target )
            return make_target
        return None

    def build_target( self, make_target_obj ):

        if make_target_obj == None: return

        if len( make_target_obj.children ) > 0:
            for c in make_target_obj.children:
                self.build_target( c )

        make_target_obj.build.execute()


    def run_build( self, out_path ):
        self.config.evaluate()

        target = self.create_target_recursively( out_path )
        if target:
            self.build_target( target )
    
    def set_default_build( self, out_path ):
        pass

    def run( self ):
        pass


def test_make():

    # Create config.
    config = Config()
    config.set_var( "CCMAKE_OUT", r'.\test\ccout' )
    config.set_var( "INCLUDE", r'.\test' )
    #config.set_var( "CXX", r'e:\Projects\techgroup_oldgen\VCLIBRARY\win32dx\bin\win32dx\cl.exe' )
    config.set_var( "CXX", r'cl.exe' )
    config.set_var( "CFLAGS_DEBUG", "/nologo /Zi /W4 /WX /GR- /D_CRT_SECURE_NO_WARNINGS /DDEBUG /Fd$(target).pdb" )
    config.set_var( "LDFLAGS", "/DEBUG /libpath:$(BUILDDIR) /LTCG /OPT:REF /OPT:ICF" )

    config.set_cmd( "CPP_COMPILE_DEBUG", "$(CXX)", "$(CFLAGS_DEBUG) -c $(source) /Fo$(target)" )
    config.set_cmd( "LINK", "$(CXX)", "$(source) /nologo /link $(LDFLAGS) /out:$(target)" )

    make_debug = Make( "debug", config )

    # make_debug.add_build( "CPP_COMPILE_DEBUG", r".\test\ccout\foo.obj", r".\test\foo.cpp", ccmake_find_include_files( r".\test\foo.cpp" )  )
    # make_debug.add_build( "CPP_COMPILE_DEBUG", r".\test\ccout\main.obj", r".\test\main.cpp", ccmake_find_include_files( r".\test\main.cpp" ) )
    
    build_list = make_debug.add_builds_from_dir( "CPP_COMPILE_DEBUG", r".\test\ccout", 'obj', r'.\test', 'cpp' )
    build_objects = []
    for b in build_list:
        build_objects += b.targets

    make_debug.add_build( "LINK", r".\test\ccout\test.exe", build_objects )
    make_debug.run_build( r".\test\ccout\test.exe" )



if __name__ == '__main__':
    test_make()
