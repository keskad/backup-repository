<?php declare(strict_types=1);

namespace App\Domain\Storage\Form;

use App\Domain\Storage\Entity\StoredFile;

class UploadByPostForm extends UploadForm
{
    /**
     * @var string
     */
    public $fileName;

    /**
     * Is this file name a final, and should not be changed?
     * Used at least in replication.
     */
    public bool $isFinalFilename = false;

    public static function createFromFile(StoredFile $file): UploadByPostForm
    {
        /**
         * @var $form UploadByPostForm
         */
        $form = parent::createFromFile($file);
        $form->fileName = $file->getFilename();

        return $form;
    }

    public function toArray(): array
    {
        $asArray = parent::toArray();
        $asArray['fileName'] = $this->fileName;

        return $asArray;
    }
}
