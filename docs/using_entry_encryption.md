# Entry encryption

## What is it?

The collected data is stored in a database. This database should obviously be encrypted, which
is a standard feature cloud platforms provide (see [aws](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html), [azure](https://docs.microsoft.com/en-us/azure/azure-sql/database/security-overview), [gcp](https://cloud.google.com/sql/faq#encryption) documentation for more details).

Entry encryption is a feature of OSD2F that works as an additional layer of protection. Donations are
stored in a per-row fashion, having a couple of metadata columns (including the `submission id`, `timestamp` and `filename`) apart from a 'blob' field that contains the actual donation called the `entry`. Entry encryption takes this potentially sensitive field and encrypts it before storing it in the database. By doing so, even if someone would get access to the database, the content of donations would be unusable.

## How to enable entry encryption

You can enable entry encryption by providing a passphrase either through the commandline or as an environment variable.

```bash
OSD2F_SECRET=secret \
OSD2F_BASIC_AUTH="user;pass" \
OSD2F_ENTRY_SECRET=TESTSECRET \
osd2f -db sqlite://encryption.db -m Development
```

Entries will now be encrypted before storage and decrypted before download (so researchers do not notice the difference). You can see the encryption by uploading some data and checking your database.

### Disabling decryption on download & local decryption

In some use-cases, you might want to keep entries decrypted for downloads. This means the files downloaded by a researcher only contain readable metadata. 

You can do so by providing a cli flag or environment variable:

```bash
OSD2F_SECRET=secret \
OSD2F_BASIC_AUTH="user;pass" \
OSD2F_ENTRY_SECRET=TESTSECRET \
OSD2F_ENTRY_DECRYPT_ON_READ=false \
osd2f -db sqlite://encryption.db -m Development
```

If you go to the researcher page and download the `json` file of submissions, they will look something like this:

>{"db_id": 1, "submission_id": "test", "filename": "ads_clicked.json", "n_deleted_across_file": 0, "insert_timestamp": "2021-10-22T12:46:47.544248+00:00", "entry": {"encrypted": "gAAAAABhcrK3qYMvBJeTyQWm-d_mKABeiNsRP49-UTaRphxjecNtJDuidYeCNZ-pWUPTRRpfdIh_48iVEqC5QawHBjnp1iw11nAOlCUR4M9nkqbkn-BATurrGJ8OV7zxbdcU6sgzeGAW2Ntgky5o0e4ozV-o66t1AmF2Kp5bc4xa--UcejOBMZjyoItNI-fD12WJxRlUpK_kkSMkZsixjLtUS0ADzonjLw=="}}, {"db_id": 2, "submission_id": "test", "filename": "ads_clicked.json", "n_deleted_across_file": 0, "insert_timestamp": "2021-10-22T12:46:47.544498+00:00", "entry": {"encrypted": "gAAAAABhcrK...

Researchers can locally decrypt the entries if they have OSD2F installed. They can do so by running:

```bash
osd2f-decrypt-submissions osd2f_completed_submissions.json decrypted_submissions.json TESTSECRET
```

The `decrypted_submissions.json` file should look something like this:

> [{"db_id": 1, "submission_id": "test", "filename": "ads_clicked.json", "n_deleted_across_file": 0, "insert_timestamp": "2021-10-22T12:46:47.544248+00:00", "entry": {"activity": "click", "ad_title": "Organic global Graphical User Interface", "timestamp": 1628971624}}, {"db_id": 2, "submission_id": "test", "filename": "ads_clicked.json", "n_deleted_across_file": 0, "insert_timestamp": "2021-10-22T12:46:47.544498+00:00", "entry": {"activity": "expand", "ad_title": "Upgradable scalable throughput", "timestamp": 1589681049}}, {"db_id": 3, "submission_id": "test", "filename": "ads_clicked.json", "n_deleted_across_file": 0, "insert_timestamp": "2021-10-22T12:46:47.544694+00:00", "entry": {"activity": "watch", "ad_title": "Organized asynchronous challenge", "timestamp": 1625135602}}, ....

## Notes

The entry encryption secret value supports the same secret store functionality as other setting fields, see [using secret stores](./using_secret_stores.md)