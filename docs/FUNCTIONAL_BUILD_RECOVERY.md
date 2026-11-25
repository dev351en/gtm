# Functional build publication record

The preserved playable build uses SDCraftCore `1.0.3-r4-functional-candidate` and the native `INDRAPRASTHA_128_V1` assets.

## Verified runtime inputs

| File | SHA-256 |
| --- | --- |
| SDCraftCore-1.0.3-r4-functional-candidate.jar | b7c76cd3a664e1bb7e1e56fd2098f7ef0a71e921d47170ed10c4e658974715af |
| GTM_Local_Java.zip | 5b5e132a2c670b07e8c0c389e086bd2dee1002ed7de72a6bdcd93acc6d6cba9a |
| gtm-launcher.jar | 904de2c6394bfd20b00152a28936a520e9e1dba8e8dec05633ee09b6f47851b1 |

The private owner package was preserved and recovered byte-for-byte. It uses the sanitized public city snapshot dated 2026-11-23, with the local workshop profile. It is not the current private Daytona world.

## Source recovery status

The previous temporary checkout recorded commit `628c01bcd7ed5d95b21c9ea049990346135a0604`, but that commit was not pushed and the checkout is no longer present. The preserved package contains compiled core and launcher files, runtime assets and verification documents. It does not contain the corresponding latest core/launcher source or tests.

Do not describe an older source build as a rebuild of this preserved binary. Do not claim that the missing commit or all of its source changes have been published. The prior source digest is retained only as evidence; it cannot reconstruct missing source bytes.

## Launch and deployment scope

`Start-Daytona.bat` connects to the existing Daytona sandbox when the owner supplies local credentials and the existing server is running. It does not deploy these binaries, start a replacement server, alter accounts, or overwrite a world.

The portable `Start-GTM-Java-Only.bat` starts the exported local world. It does not connect to the live Daytona server. Downloading a repository source ZIP is not equivalent to downloading that assembled runtime package.

The earlier saved verification includes actual Linux Paper startup, authentication, pack serving and a clean stop. Native Windows execution, native Java/Bedrock client rendering, and deployment to the existing private Daytona instance remain unverified. The complete Revision 4 city/campaign is not finished.

