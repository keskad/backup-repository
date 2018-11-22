<?php declare(strict_types=1);

namespace App\Controller\Storage;

use App\Controller\BaseController;
use App\Domain\Storage\ActionHandler\ViewFileHandler;
use App\Domain\Storage\Factory\Context\SecurityContextFactory;
use App\Domain\Storage\Form\ViewFileForm;
use App\Infrastructure\Storage\Form\ViewFileFormType;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\StreamedResponse;

class ViewFileController extends BaseController
{
    /**
     * @var ViewFileHandler
     */
    private $handler;

    /**
     * @var SecurityContextFactory
     */
    private $authFactory;

    public function __construct(ViewFileHandler $handler, SecurityContextFactory $authFactory)
    {
        $this->handler = $handler;
        $this->authFactory = $authFactory;
    }

    public function handle(Request $request, string $filename): Response
    {
        $form = new ViewFileForm();
        $form->filename = $filename;
        $infrastructureForm = $this->submitFormFromRequestQuery($request, $form, ViewFileFormType::class);

        if (!$infrastructureForm->isValid()) {
            return $this->createValidationErrorResponse($infrastructureForm);
        }

        return $this->wrap(
            function () use ($form) {
                $response = $this->handler->handle(
                    $form,
                    $this->authFactory->createViewingContextFromTokenAndForm($this->getLoggedUserToken(), $form)
                );

                if ($response->getCode() === Response::HTTP_OK) {
                    return new StreamedResponse($response->getResponseCallback());
                }

                return new JsonResponse($response, $response->getCode());
            }
        );
    }
}
