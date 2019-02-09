

from ..entity.encryption import Encryption
from ..entity.access import ServerAccess
from ..entity.definition import BackupDefinition
from ..mapping.definitions import DefinitionsMapping
from ..exceptions import DefinitionFactoryException


class DefinitionFactory:
    """ Constructs objects basing on the configuration file """

    _accesses = {}    # type: dict[ServerAccess]
    _encryption = {}  # type: dict[Encryption]
    _backups = {}     # type: dict[BackupDefinition]
    _debug = False    # type: bool

    def __init__(self, configuration: dict, debug: bool):
        self._debug = debug
        self._parse(configuration)

    def _parse(self, config: dict):
        self._parse_accesses(config['accesses'])
        self._parse_encryption(config['encryption'])
        self._parse_backups(config['backups'])

    def _parse_accesses(self, config: dict):
        for key, values in config.items():
            with DefinitionFactoryErrorCatcher('accesses.' + key, self._debug):
                self._accesses[key] = ServerAccess.from_config(values)

    def _parse_encryption(self, config: dict):
        for key, values in config.items():
            with DefinitionFactoryErrorCatcher('encryption.' + key, self._debug):
                self._encryption[key] = Encryption.from_config(values)

    def _parse_backups(self, config: dict):
        for key, values in config.items():
            with DefinitionFactoryErrorCatcher('backups.' + key, self._debug):

                # find related access and encryption
                values['access'] = self._accesses[values['access']]

                if "encryption" in values:
                    values['encryption'] = self._encryption[values['encryption']]

                factory_method = DefinitionsMapping.get(values['type'])
                self._backups[key] = factory_method.from_config(values)

    def get_definition(self, name: str) -> BackupDefinition:

        if name not in self._backups:
            raise DefinitionFactoryException(
                'No such backup definition, maybe a typo? Please check the configuration file'
            )

        return self._backups[name]


class DefinitionFactoryErrorCatcher:
    _key_name = ""
    _debug = False

    def __init__(self, config_key_name: str, _debug: bool):
        self._key_name = config_key_name
        self._debug = _debug

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if self._debug:
                return

            raise DefinitionFactoryException(
                ' ERROR: There was a problem during parsing the configuration at section "' +
                self._key_name + '" in key ' + str(exc_val) + ', details: ' + str(exc_type))

