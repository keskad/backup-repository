
from .fileordirectorybackup import FileOrDirectoryBackup
from ..entity.definition.docker import DockerOfflineVolumesDefinition
from ..result import CommandExecutionResult


class DockerVolumeHotBackup(FileOrDirectoryBackup):
    """
<sphinx>
docker_hot_volumes
------------------

Alias to "path" with enforced container parameter.

Backups a RUNNING container. For some applications it may be safe to backup a running container, for some not.
See DockerVolumesBackup and adjust backup method to the application you want to keep safe.
Gets into the container and makes a backup of directories into a single tar file.

**Example:**

.. code:: yaml

    docker_hot_volumes_example:
        type: docker_hot_volumes
        container: "test_www"
        access: backup_one
        encryption: none
        collection_id: "${COLLECTION_ID}"
        paths:
            - /var/www
            - /var/log/nginx/access.log

        # optional
        #tar_pack_cmd: "tar -czf %stdin% %paths%"
        #tar_unpack_cmd: "tar -xzf %stdin% %target%"
        #docker_bin: "sudo docker"

</sphinx>
    """

    def is_using_container(self) -> bool:
        return True


class DockerVolumeBackup(DockerVolumeHotBackup):
    """
docker_volumes
--------------

Offline docker container backup. Runs a new container, mounts volumes of origin container and performs a backup
of those mounted volumes. Fully secure option for all kind of applications, as the applications are shut down for
a moment.

Notice: Your applications will have a downtime. Be careful about dependent services, those may exit unexpectedly.

**Example:**

.. code:: yaml

    www_docker_offline:
        type: docker_volumes
        container: "test_www"
        access: backup_one
        encryption: enc1
        collection_id: "${COLLECTION_ID}"
        paths:
            - /etc
            - /var/lib/mysql
            - /var/log/mysql.log

        # optional
        docker_bin: "docker"
        tar_pack_cmd: "tar -czf %stdin% %paths%"
        tar_unpack_cmd: "tar -xzf %stdin% %target%"
        temp_image_name: "alpine:3.9"
        temp_image_cmd: "apk add --update xz bzip2 && sleep 3600"

    """

    _container_id = ""

    def _get_definition(self) -> DockerOfflineVolumesDefinition:
        return self._definition

    def validate_before_creating_backup(self):
        # do not check if container is up, it does not need to be. It must only exists.
        pass

    def receive_backup_stream(self, container: str = None):
        self._logger.info('Performing backup of origin container in offline mode')
        temporary_container_id = self._stop_origin_and_start_temporary_containers()

        return super().receive_backup_stream(container=temporary_container_id)

    def restore_backup_from_stream(self, stream, container: str = None) -> CommandExecutionResult:
        self._logger.info('Restoring backup to the temporary container through mounted volumes of origin container')
        temporary_container_id = self._stop_origin_and_start_temporary_containers()

        return super().restore_backup_from_stream(stream, container=temporary_container_id)

    def backup_container_directories(self, docker_bin: str, container: str, paths: list,
                                     definition: DockerOfflineVolumesDefinition) -> CommandExecutionResult:
        """ Performs a backup of multiple directories using TAR with gzip/xz/bz2 compression """

        return self._execute_in_container(
            docker_bin, container,
            definition.get_pack_cmd(paths),
            definition
        )

    def _stop_origin_and_start_temporary_containers(self) -> str:
        """ Stop origin container and start a temporary container """

        # @todo: Support linked/dependent containers

        definition = self._get_definition()

        self._logger.info('Stopping origin container')
        self._stop_container(definition.get_docker_bin(), definition.get_container())

        self._logger.info('Spawning temporary container with volumes from origin container')
        self._container_id = self._spawn_temporary_container(
            definition.get_docker_bin(),
            definition.get_container(),
            definition.get_temp_image_name(),
            definition.get_temp_cmd()
        )

        return self._container_id

    def _finalize(self, action: str):
        definition = self._get_definition()

        try:
            self._logger.info('Killing temporary container')
            self._kill_container(definition.get_docker_bin(), self._container_id)

        except Exception:
            self._logger.warning('Cannot kill temporary container "' + self._container_id + '"')

        # @todo: Support linked/dependent containers

        self._logger.info('Starting origin container')
        self._start_container(definition.get_docker_bin(), definition.get_container())
