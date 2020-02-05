<?php declare(strict_types=1);

namespace App\Infrastructure\Common\Test\Database;

use Doctrine\DBAL\Connection;
use Doctrine\DBAL\Driver\PDOConnection;
use Doctrine\DBAL\Driver\PDOPgSql\Driver;

/**
 * Backup & Restore of the database - used in tests
 */
class PostgresRestoreDB implements RestoreDBInterface
{
    /**
     * @var Connection
     */
    private $connection;

    public function __construct(Connection $connection)
    {
        $this->connection = $connection;
    }

    private function createBackupDatabaseName(): string
    {
        $currentDbName = $this->connection->getDatabase();

        return $currentDbName . '_bckp';
    }

    public function backup(): bool
    {
        $currentDbName = $this->connection->getDatabase();
        $backupDbName = $this->createBackupDatabaseName();

        $this->commit($this->connection);
        $this->connection->exec('DROP DATABASE IF EXISTS "' . $backupDbName . '";');
        $this->connection->exec('CREATE DATABASE "' . $backupDbName . '" TEMPLATE "' . $currentDbName . '";');

        return true;
    }

    public function restore(): bool
    {
        $currentDbName = $this->connection->getDatabase();
        $backupDbName = $this->createBackupDatabaseName();

        $this->connection->close();
        $this->dropAndCreate(
            $currentDbName,
            $backupDbName,
            $this->connection->getParams()
        );
        $this->connection->connect();

        return true;
    }

    public function canRestore(): bool
    {
        $backupDbName = $this->createBackupDatabaseName();
        $cursor = $this->connection->executeQuery("SELECT 1 FROM pg_database WHERE datname='" . $backupDbName . "'");

        return (int) $cursor->fetch(\Doctrine\DBAL\FetchMode::COLUMN) === 1;
    }

    private function dropAndCreate(string $toRecreate, string $template, array $doctrineParams): void
    {
        // cannot drop currently used database
        $doctrineParams['dbname'] = 'postgres';

        $driver = new Driver();
        $pdo = $driver->connect($doctrineParams, $doctrineParams['user'], $doctrineParams['password']);

        $this->commit($pdo);
        $pdo->exec('DROP DATABASE IF EXISTS "' . $toRecreate . '";');
        $pdo->exec('CREATE DATABASE "' . $toRecreate . '" TEMPLATE "' . $template . '";');
    }

    /**
     * @param PDOConnection|Connection $connection
     */
    private function commit($connection): void
    {
        try {
            $connection->commit();
        } catch (\Exception $exception) {

        }
    }
}
