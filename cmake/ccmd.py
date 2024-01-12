"""
    pycmake ccmd module
    --------------------

    Copyright (C) 2023 jppgmx
    Licensed under MIT License

    Contains the commands that are passed to cmake.
"""

from abc import ABC, abstractmethod

from cmake.cbasic import CMakeValType, CMakeValue
from cmake import coptions as ops
from cmake.coptions import CMakeBaseOption

from cmakeutils.typecheck import isdict

class CMakeCommand(ABC):
    """
        Base class to implement all cmake commands such as configure, build and install.

        Not all options are implemented in every command, only some that are "main".
        Option values are passed into the constructor as a name/value dictionary.
    """

    commandName: str
    __options__: dict[ops.CMakeBaseOption, CMakeValue] = None

    def __init__(self, **kwargs):
        self.__options__ = self.get_options()

        for key, val in kwargs.items():
            for def_op in self.__options__.keys():
                if key == def_op.name:
                    value = CMakeValue(val)
                    if def_op.type != value.type:
                        raise ValueError(f'Incompatible types between value ({value.type})' +
                                         f'and option {def_op.name} ({def_op.type})')
                    self.__options__[def_op] = value



    @abstractmethod
    def get_options(self) -> dict[ops.CMakeBaseOption,]:
        """
            Returns a dictionary containing the command options to be assigned.
        """

    def validate(self):
        """
            Validates the values assigned to the options.
        """
        for option, value in self.__options__.items():
            if value is not None:
                if value.type != option.type:
                    raise ValueError('Invalid value type for option "' + option.name + '": '
                                     + value.type)

    def compile(self) -> list[str]:
        """
            Compiles each option value into a single list of arguments
            to be passed to the executable.
        """

        _args = []
        for option, value in self.__options__.items():
            compval = list(option.compile(value))
            _args += compval

        return _args

    def __getitem__(self, key: str) -> str | bool | dict[str, CMakeValue]:
        if not isinstance(key, str):
            raise ValueError('key must be a str.')

        selop = None
        for option in self.__options__:
            if option.name.lower() == key.lower():
                selop = option
                break

        if selop is None:
            raise KeyError('option not found: ' + key)

        opvalue = self.__options__[selop]
        return None if opvalue is None else opvalue.value

    def __setitem__(self, key, value):
        if not isinstance(value, (str, bool)) and not isdict(value, str, CMakeValue):
            raise ValueError('value must be a str, bool or dict[str, str].')

        selop = None
        for option in self.__options__:
            if option.name.lower() == key.lower():
                selop = option
                break

        if selop is None:
            raise KeyError('option not found: ' + key)

        val = CMakeValue(value)
        if selop.type != val.type:
            raise ValueError('Incompatible types between option ' + selop.name +
                             f'({selop.type}) and value ({val.type}).')

        self.__options__[selop] = val

class CMakeConfigure(CMakeCommand):
    """
        Implementation of the configure command.

        Options
        -------

        'source_dir': Path to source dir. (default: '.')
        'build_dir': Path to build dir. (default: build)
        'generator': Specify a build system generator. (default: Ninja)

        'initial_cache': (Optional) Pre-load a script to populate the cache..
        'toolset_spec': (Optional) Toolset specification for the generator, if supported.
        'platform_name': (Optional) Specify platform name if supported by generator.
        'toolchain': (Optional) Specify the cross compiling toolchain file.
        'install_prefix': (Optional) Specify the installation directory.

        'variables': (Optional) A dictionary of variables to set.
        'remove_vars': (Optional) A dictionary of variables to unset. (Set value to None by default)

        There are more options besides these, 
        see https://cmake.org/cmake/help/latest/manual/cmake.1.html and 
        pass by calling the invoke method.
    """

    commandName: str = 'configure'
    __generators__ = [
        'Ninja', 
        'MinGW Makefiles', 
        'Visual Studio 16 2019', 
        'Visual Studio 17 2022',
        'Unix Makefiles'
        ]

    def get_options(self) -> dict[ops.CMakeBaseOption,]:
        return {
            ops.CMakeSimpleOption('source_dir', '-S',
                                  '{option}{ssp}{value}', CMakeValType.STRING, '.'): None,

            ops.CMakeSimpleOption('build_dir', '-B',
                                  '{option}{ssp}{value}', CMakeValType.STRING, 'build'): None,

            ops.CMakeSimpleOption('generator', '-G',
                                  '{option}{ssp}{value}', CMakeValType.STRING, 'Ninja'): None,

            ops.CMakeOptionalSimpleOption('initial_cache', '-C',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeOptionalSimpleOption('toolset_spec', '-T',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeOptionalSimpleOption('platform_name', '-A',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeOptionalSimpleOption('toolchain', '--toolchain',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeOptionalSimpleOption('install_prefix', '--install-prefix',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeVariablesOption(): None,
            ops.CMakeVariablesOption(True): None
        }

class CMakeBuildCommand(CMakeCommand):
    """
        Implementation of the build command.

        Options
        -------

        'build_path': Project binary directory to be built. (default: '.')

        'max_jobs': (Optional) The maximum number of concurrent processes to use when building.
        'configuration': (Optional) For multi-configuration tools, choose configuration.
        'verbose': (Optional) Enable verbose output if supported.

        There are more options besides these, 
        see https://cmake.org/cmake/help/latest/manual/cmake.1.html and 
        pass by calling the invoke method.
    """

    commandName: str = 'build'

    def get_options(self) -> dict[ops.CMakeBaseOption,]:
        return {
            ops.CMakeSimpleOption('build_path', '--build',
                                  '{option}{ssp}{value}', CMakeValType.STRING, '.'): None,

            ops.CMakeOptionalSimpleOption('max_jobs', '-j',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeOptionalSimpleOption('configuration', '--config',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeSwitchOption('verbose', '-v', False): None
        }

class CMakeInstallCommand(CMakeCommand):

    """
        Implementation of the install command.

        Options
        -------

        'install_path': Project binary directory to install. (default: '_install')

        'configuration': (Optional) For multi-configuration generators, choose configuration.
        'component': (Optional) Component-based install. Only install specified component.

        'default_dir_perms': (Optional) Default directory install permissions. 
                                        Permissions in format <u=rwx,g=rx,o=rx>.

        'prefix': (Optional) Override the installation prefix, CMAKE_INSTALL_PREFIX.
        'verbose': (Optional) Enable verbose output.
        'strip': (Optional) Strip before installing.
    """
    commandName: str = 'install'

    def get_options(self) -> dict[CMakeBaseOption,]:
        return {
            ops.CMakeSimpleOption('install_path', '--install',
                                  '{option}{ssp}{value}', CMakeValType.STRING, '_install'): None,

            ops.CMakeOptionalSimpleOption('configuration', '--config',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeOptionalSimpleOption('component', '--component',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeOptionalSimpleOption('default_dir_perms', '--default-directory-permissions',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeOptionalSimpleOption('prefix', '--prefix',
                                          '{option}{ssp}{value}', CMakeValType.STRING): None,

            ops.CMakeSwitchOption('verbose', '-v', False): None,
            ops.CMakeSwitchOption('strip', '--strip', False): None
        }
