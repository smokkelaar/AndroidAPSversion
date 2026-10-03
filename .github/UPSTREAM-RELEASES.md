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
in gebruik. Upstream-tags en branches worden rechtstreeks uitgecheckt op hun
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
Overige nieuwe tags komen bij de volgende controle aan bod. Releases worden bewaard.
Automatische en handmatige builds markeren releases niet als GitHub's algemene Latest.

De bestaande handmatige AAPS-, Branch-, PR- en Cherry Pick-workflows publiceren
nu ook naar GitHub Releases, onder `manual-<run-id>`, als prerelease. Hun variantkeuze
blijft beschikbaar. Geen van deze workflows gebruikt nog Google Drive.

## Vereisten

GitHub Actions moet ingeschakeld zijn. De bestaande `KEYSTORE_SET` of afzonderlijke
`KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_ALIAS` en `KEY_PASSWORD` secrets zijn nodig.
`GDRIVE_OAUTH2` is niet meer nodig. Publicatie gebruikt de ingebouwde `GITHUB_TOKEN`
met `contents: write`; een extra persoonlijk toegangstoken is niet nodig.

GitHub-planning kan vertraging hebben. In openbare repositories schakelt GitHub
geplande workflows na 60 dagen zonder repositoryactiviteit uit; schakel de workflow
dan opnieuw in via Actions. Zie [GitHub's documentatie over schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Plannercontroles: `python -m unittest discover -s .github/scripts -p 'test_*.py'`.
