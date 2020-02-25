<?php declare(strict_types=1);

namespace App\Controller\Storage;

use App\Controller\BaseController;
use App\Domain\Storage\ActionHandler\FilesListingHandler;
use App\Domain\Storage\Factory\Context\SecurityContextFactory;
use App\Domain\Storage\Form\FilesListingForm;
use App\Infrastructure\Common\Http\JsonFormattedResponse;
use App\Infrastructure\Storage\Form\FilesListingFormType;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

class FilesListingController extends BaseController
{
    private FilesListingHandler $handler;
    private SecurityContextFactory $authFactory;

    public function __construct(FilesListingHandler $handler, SecurityContextFactory $authFactory)
    {
        $this->handler = $handler;
        $this->authFactory = $authFactory;
    }

    /**
     * @param Request $request
     *
     * @return Response
     *
     * @throws \Exception
     */
    public function handleListing(Request $request): Response
    {
        $form = new FilesListingForm();
        $infrastructureForm = $this->submitFormFromRequestQuery($request, $form, FilesListingFormType::class);

        if (!$infrastructureForm->isValid()) {
            return $this->createValidationErrorResponse($infrastructureForm);
        }

        $securityContext = $this->authFactory
            ->createListingContextFromTokenAndForm($this->getLoggedUserToken(), $form);

        return $this->wrap(
            function () use ($form, $securityContext) {
                return new JsonFormattedResponse(
                    $this->handler->handle(
                        $form,
                        $securityContext
                    ),
                    JsonFormattedResponse::HTTP_OK
                );
            }
        );
    }
}
