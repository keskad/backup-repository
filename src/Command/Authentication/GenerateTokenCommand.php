<?php declare(strict_types=1);

namespace App\Command\Authentication;

use App\Domain\Authentication\ActionHandler\TokenGenerationHandler;
use App\Domain\Authentication\Form\AuthForm;
use App\Domain\Authentication\Form\TokenDetailsForm;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Output\OutputInterface;

class GenerateTokenCommand extends Command
{
    /**
     * @var TokenGenerationHandler
     */
    private $handler;

    public function __construct(TokenGenerationHandler $handler)
    {
        $this->handler = $handler;

        parent::__construct();
    }

    protected function configure()
    {
        $this->setName('auth:create-token')
            ->setDescription('Creates an authentication token')
            ->addOption('roles', null, InputOption::VALUE_REQUIRED)
            ->addOption('tags', null, InputOption::VALUE_REQUIRED)
            ->addOption('mimes', null, InputOption::VALUE_REQUIRED)
            ->setHelp('Allows to generate a token you can use later to authenticate in application for a specific thing');
    }

    protected function execute(InputInterface $input, OutputInterface $output)
    {
        $form = new AuthForm();
        $form->data = new TokenDetailsForm();
        $form->data->tags             = $this->getMultipleValueOption($input, 'tags');
        $form->data->allowedMimeTypes = $this->getMultipleValueOption($input, 'mimes');
        $form->roles                  = $this->getMultipleValueOption($input, 'roles');

        $output->writeln('Form:');
        $output->writeln('========================');

        foreach ($form->data->tags as $tag) {
            $output->writeln(' [Tag] -> ' . $tag);
        }

        foreach ($form->data->allowedMimeTypes as $mimes) {
            $output->writeln(' [Mime] -> ' . $mimes);
        }

        foreach ($form->roles as $role) {
            $output->writeln(' [Role] -> ' . $role);
        }

        $response = $this->handler->handle($form);

        $output->writeln("\nResponse:");
        $output->writeln('========================');
        $output->writeln(json_encode($response, JSON_PRETTY_PRINT));
    }

    private function getMultipleValueOption(InputInterface $input, string $optionName): array
    {
        $values = explode(',', $input->getOption($optionName) ?: '');
        $values = array_filter($values);

        return $values;
    }
}