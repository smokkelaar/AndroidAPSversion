# Herstelde builds voor Android 7 en 8

Deze herstelroute geldt alleen voor de twee commits die in `restore_legacy.py`
zijn vastgelegd. Android-eisen, AAPS-versiecontrole en doseringscode blijven intact.

- Android 8: upstream `v2.8.2.1`, commit
  `fb9325384e96cdf3b508468584156aa9971638da`; geen gewijzigde AAPS-bronbestanden.
- Android 7: [compat-2.6.2](https://github.com/smokkelaar/AndroidAPSversion/tree/03ce42fc4c8e622f8c5619312ad17d0421b67523),
  afgeleid van upstream-tag `2.6.2`, commit
  `972fdbfe9e40853afc09eb06f83045c95acfb53c`. De volledige wijziging staat in
  `android7.patch`: de verdwenen Fabric-buildplugin en de Jacoco-plugin voor
  testdekking verwijderd. Beide zijn buildgereedschap; de release-APK gebruikt
  geen testdekking. De volledige wijziging betreft uitsluitend Gradle-bestanden.
  De runtime-SDK blijft behouden. De init-configuratie levert het build-ID dat
  deze plugin voorheen genereerde. De oude Fabric-rapportagedienst is beëindigd.

Beide builds gebruiken twee herbouwde UI-bibliotheken vanuit de oorspronkelijke
repositories, beschikbaar via JitPack, en een gearchiveerde Wear-bibliotheek:

- [Google Flexbox 0.3.0](https://github.com/google/flexbox-layout/tree/99a4b6649c16d2b34fb6a2ac14180f76f01b38f3).
- [TextDrawable](https://github.com/amulyakhare/TextDrawable/tree/558677ea316e60346948b381e5e274f49b00d370),
  op het vastgelegde broncommit van de oorspronkelijke auteur. Dit is een
  herbouwde bibliotheek, geen bewijs van byte-identiteit met het verdwenen
  JCenter-bestand `1.0.1`.
- [WearPreferenceActivity 0.5.0](https://github.com/denley/WearPreferenceActivity/tree/49eec136a52a6a4ff97390ed684fc5fb88c4fd60):
  de oude AAR en POM zijn beschikbaar via de Appodeal Maven-mirror. Dit is een
  externe archiefkopie; de oorspronkelijke auteur heeft geen checksum gepubliceerd
  waarmee byte-identiteit onafhankelijk kan worden bewezen. AAR en POM zijn beide
  op SHA-256 vastgelegd. De POM blijft intact, inclusief de wearable-afhankelijkheid.

De controller controleert de SHA-256 van alle drie AAR-bestanden voordat Gradle ze
via een tijdelijke lokale Maven-repository kan gebruiken. Een gewijzigde download
of een andere broncommit wordt geweigerd. De init-configuratie staat buiten de
AAPS-broncheckout en bevat uitsluitend repositoryconfiguratie en het Fabric-build-ID.

De builds hebben geen private ondertekeningssleutels. APK's worden op een aparte
runner uitgelijnd, ondertekend en gecontroleerd. De release vermeldt de gebruikte
bronvariant en herstelroute. Herstelde builds worden als prerelease gepubliceerd;
een geslaagde build vervangt geen controle op het beoogde toestel.
