# Herstelde builds voor Android 7 en 8

Deze herstelroute geldt alleen voor de twee commits die in `restore_legacy.py`
zijn vastgelegd. Android-eisen, AAPS-versiecontrole en doseringscode blijven intact.

- Android 8: upstream `v2.8.2.1`, commit
  `fb9325384e96cdf3b508468584156aa9971638da`; geen gewijzigde AAPS-bronbestanden.
- Android 7: [compat-2.6.2](https://github.com/smokkelaar/AndroidAPSversion/tree/408329db4c833c47bafe4c7971fdbc1d5dc076ce),
  afgeleid van upstream-tag `2.6.2`, commit
  `972fdbfe9e40853afc09eb06f83045c95acfb53c`. De volledige wijziging staat in
  `android7.patch`: drie regels voor de verdwenen Fabric-buildplugin verwijderd.
  De runtime-SDK blijft behouden. De init-configuratie levert het build-ID dat
  deze plugin voorheen genereerde. De oude Fabric-rapportagedienst is beëindigd.

Beide builds gebruiken twee herbouwde UI-bibliotheken vanuit de oorspronkelijke
repositories, beschikbaar via JitPack:

- [Google Flexbox 0.3.0](https://github.com/google/flexbox-layout/tree/99a4b6649c16d2b34fb6a2ac14180f76f01b38f3).
- [TextDrawable](https://github.com/amulyakhare/TextDrawable/tree/558677ea316e60346948b381e5e274f49b00d370),
  op het vastgelegde broncommit van de oorspronkelijke auteur. Dit is een
  herbouwde bibliotheek, geen bewijs van byte-identiteit met het verdwenen
  JCenter-bestand `1.0.1`.

De controller controleert de SHA-256 van beide AAR-bestanden voordat Gradle ze
via een tijdelijke lokale Maven-repository kan gebruiken. Een gewijzigde download
of een andere broncommit wordt geweigerd. De init-configuratie staat buiten de
AAPS-broncheckout en bevat uitsluitend repositoryconfiguratie en het Fabric-build-ID.

De builds hebben geen private ondertekeningssleutels. APK's worden op een aparte
runner uitgelijnd, ondertekend en gecontroleerd. De release vermeldt de gebruikte
bronvariant en herstelroute. Herstelde builds worden als prerelease gepubliceerd;
een geslaagde build vervangt geen controle op het beoogde toestel.
