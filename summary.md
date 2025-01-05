- Identified and fixed a logical error regarding the verification process for projects. The changes ensured that when a project is in the "Implemented" state and the termination document is signed, it can move forward to the verification stage. Additionally, change requests were restricted to situations where the termination document was not created. I'm waiting for the review. [MR #943](https://gitlab.com/stekz/stx-ndp/ndp-platform/-/merge_requests/943)

- Introduced a new process that allows only the relevant parts of the project to enter a specific status. This has been successfully merged to the main branch. [MR #942](https://gitlab.com/stekz/stx-ndp/ndp-platform/-/merge_requests/942)

- Fixed the process to ensure that entry is allowed only when possible. This change has been successfully merged to the main branch. [MR #941](https://gitlab.com/stekz/stx-ndp/ndp-platform/-/merge_requests/941)

- Implemented a fix to ensure that the site is correctly identified as being on the STX domain. I'm waiting for the review. [MR #940](https://gitlab.com/stekz/stx-ndp/ndp-platform/-/merge_requests/940)

- Resolved issues related to the management of project data for partners. This has been successfully merged to the main branch. [MR #936](https://gitlab.com/stekz/stx-ndp/ndp-platform/-/merge_requests/936)

- The button for uploading the Authorization and Data Statement document was disabled when the status was "Entered in backoffice." [Issue #609](https://gitlab.com/stekz/stx-ndp/ndp-platform/-/issues/609)

- The project status was automatically updated to "entered" after at least one Project Part was available. An MR was created for this. [Issue #608](https://gitlab.com/stekz/stx-ndp/ndp-platform/-/issues/608)

- The logic to ensure the site was on the STX domain was fixed. An MR was created for this. [Issue #607](https://gitlab.com/stekz/stx-ndp/ndp-platform/-/issues/607)

- The text of the third bullet on the One-pager document was changed to: "fakturę za zakup Nowego Źródła Ciepła oraz jedną fakturę (rachunek) za energię elektryczną lub ciepło lub gaz ziemny wystawioną Wnioskodawcy temu przez przedsiębiorsywo energetyczne Wnioskodawcy. Załączyć można dowolną fakturę (rachunek) wystawioną w ciągu ostatnich 3 miesięcy." [Issue #605](https://gitlab.com/stekz/stx-ndp/ndp-platform/-/issues/605)

- The feature for managing WC Project Data for Partners was completed. The project status automatically upgraded upon completing company and partner details. An MR was created for this. [Issue #602](https://gitlab.com/stekz/stx-ndp/ndp-platform/-/issues/602)