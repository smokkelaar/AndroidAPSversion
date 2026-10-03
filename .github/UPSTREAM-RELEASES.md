# Automatische upstream builds

De workflow **Upstream Releases** controleert `nightscout/AndroidAPS` elke
15 minuten op nieuwe tags en nieuwe commits op `master`, `dev` en `dev3`.
Na samenvoegen naar de standaardbranch (`master`) kan de workflow ook direct
worden gestart via Actions → Upstream Releases → Run workflow.

## Startpunt en kanalen

`.github/upstream-baseline.json` bevat de upstream-stand bij het voorbereiden
van deze wijziging. Alle toen bestaande tags worden permanent overgeslagen.
De toenmalige branchcommits worden evenmin gebouwd. Alleen veranderingen vanaf
dit startpunt leveren builds op; oude releases worden niet ingehaald.
Bewaar dit bestand: opnieuw vastleggen zou nieuwe, nog niet gebouwde versies
kunnen overslaan.

* **tags**: elke nieuwe upstream-tag levert een release op. Tags met een `-`
  in de naam (zoals ontwikkelversies) worden als prerelease gepubliceerd.
* **master**, **dev**, **dev3**: elke nieuwe waargenomen branchstand levert
  een afzonderlijke prerelease op, herkenbaar aan kanaal en volledige commit-SHA.
  Als meerdere commits tussen twee controles binnenkomen, wordt de nieuwste
  stand gebouwd. Tussengelegen commits worden niet apart gebouwd.

Iedere release bevat ondertekende **fullRelease** APK's voor telefoon en Wear.
De bestaande keystore en controle van het ondertekeningscertificaat blijven
in gebruik. Buildrunners hebben uitsluitend leesrechten en ontvangen geen
ondertekeningssleutels. De APK-bestanden gaan via Actions-artifacts naar een
nieuwe runner die ze met `zipalign` en `apksigner` ondertekent en verifieert.
Die runner checkt geen broncode uit, voert geen Gradle uit en herstelt geen
buildcaches. Alleen die runner krijgt de sleutel en publicatierechten.
Upstream-tags en branches worden rechtstreeks uitgecheckt op hun
vastgelegde commit; de fork hoeft daarvoor niet met upstream te worden gesynchroniseerd.

## Publicatie en herstel

Automatische release-tags beginnen met `upstream-tag-`, `upstream-master-`,
`upstream-dev-` of `upstream-dev3-`. De oorspronkelijke ref, broncommit en buildrun
staan in de releasebeschrijving. GitHub's automatisch gegenereerde broncodearchieven
horen bij de workflowcommit in deze fork; de APK-bron is de vermelde upstream-commit.

Een release blijft concept totdat beide APK's zijn geüpload. Alleen gepubliceerde
releases tellen als geslaagd. Een mislukte build of upload wordt bij een volgende
controle opnieuw geprobeerd; een bestaand concept wordt afgemaakt. Bij een mislukte
branchbuild kan een nieuwere branchstand de vorige poging vervangen.
Er draaien maximaal twee builds tegelijk en maximaal twintig per controle.
De branch `upstream-release-state` bewaart in `release-queue.json` welke refs
als laatste zijn geprobeerd. De twintig langst niet geprobeerde refs worden
geselecteerd; deze keuze wordt vóór de builds opgeslagen. Ook wanneer builds
mislukken voordat er een conceptrelease is gemaakt, komen latere tags aan bod.
Verwijder deze branch niet: het is de blijvende wachtrijadministratie.
Voltooide en vervangen refs worden uit deze administratie verwijderd, zodat
het bestand uitsluitend pogingen voor de actuele wachtrij bewaart.
Releases worden bewaard.
Automatische en handmatige builds markeren releases niet als GitHub's algemene Latest.

De bestaande handmatige AAPS-, Branch-, PR- en Cherry Pick-workflows publiceren
nu ook naar GitHub Releases, onder `manual-<run-id>`, als prerelease. Hun variantkeuze
blijft beschikbaar. Geen van deze workflows gebruikt nog Google Drive.

## Vereisten

GitHub Actions moet ingeschakeld zijn. De bestaande `KEYSTORE_SET` of afzonderlijke
`KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_ALIAS` en `KEY_PASSWORD` secrets zijn nodig.
`GDRIVE_OAUTH2` is niet meer nodig. Publicatie gebruikt de ingebouwde `GITHUB_TOKEN`
met `contents: write`; een extra persoonlijk toegangstoken is niet nodig.
De repositoryvariabele `UPSTREAM_RELEASES_ENABLED` moet de waarde `true` hebben
voor geplande controles. Verwijderen of op `false` zetten pauzeert de planning;
handmatige controles blijven beschikbaar. Bij reparaties blijft deze schakelaar
uit totdat de tests en review geslaagd zijn; daarna wordt hij weer ingeschakeld.

GitHub-planning kan vertraging hebben. In openbare repositories schakelt GitHub
geplande workflows na 60 dagen zonder repositoryactiviteit uit; schakel de workflow
dan opnieuw in via Actions. Zie [GitHub's documentatie over schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Regressiecontroles: `python -m unittest discover -s .github/scripts -p 'test_*.py'`
(met PyYAML). **Release Pipeline Tests** controleert ook de isolatie tussen
runners en test het ondertekenen van kleine fixture-APK's met tijdelijke sleutels.
Er worden daarbij geen oude AAPS-versies gebouwd of releases gepubliceerd.
