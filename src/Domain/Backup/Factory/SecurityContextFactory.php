<?php declare(strict_types=1);

namespace App\Domain\Backup\Factory;

use App\Domain\Authentication\Entity\Token;
use App\Domain\Backup\Security\CollectionManagementContext;
use App\Domain\Roles;

class SecurityContextFactory
{
    public function createCollectionManagementContext(Token $token): CollectionManagementContext
    {
        return new CollectionManagementContext(
            $token->hasRole(Roles::ROLE_COLLECTION_ADD)
        );
    }
}
