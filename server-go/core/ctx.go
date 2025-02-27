package core

import (
	"github.com/riotkit-org/backup-repository/collections"
	"github.com/riotkit-org/backup-repository/concurrency"
	"github.com/riotkit-org/backup-repository/config"
	"github.com/riotkit-org/backup-repository/security"
	"github.com/riotkit-org/backup-repository/storage"
	"github.com/riotkit-org/backup-repository/users"
	"gorm.io/gorm"
)

type ApplicationContainer struct {
	Db              *gorm.DB
	Config          *config.ConfigurationProvider
	Users           *users.Service
	GrantedAccesses *security.Service
	Collections     *collections.Service
	Storage         *storage.Service
	JwtSecretKey    string
	HealthCheckKey  string
	Locks           *concurrency.LocksService
}
