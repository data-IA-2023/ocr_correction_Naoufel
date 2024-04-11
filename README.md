# ocr_correction_Naoufel projet Vision OCR

# variables d'environnements:
**OCR_API**: API invoice
**VISION_KEY**:azur clef de connexion
**VISION_ENDPOINT**:azur lien de connexion
**DATABASE_URL**:lien de la BDD
**DISCORD_OCR**:intégration discord


# COMMANDES DOCKER

**creation docker**:docker build -t NAME .

**imagedocker**:docker run -p 3000:3000 -e MYVAR=XXX -e (variable d'environnement=Value) --name NAME NAME

**dockerimageencour**:docker images

**supprimer une image**:docker rm NAME


