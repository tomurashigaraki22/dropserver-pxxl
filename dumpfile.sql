USE 'digihafe_dropapp'

CREATE TABLE "driver_location" (
  "id" int NOT NULL AUTO_INCREMENT,
  "email" varchar(80) NOT NULL,
  "latitude" decimal(10,8) NOT NULL DEFAULT '0.00000000',
  "longitude" decimal(11,8) NOT NULL DEFAULT '0.00000000',
  "user_type" varchar(80) NOT NULL,
  PRIMARY KEY ("id")
);

CREATE TABLE "driver_rides" (
  "id" int NOT NULL AUTO_INCREMENT,
  "email" varchar(80) NOT NULL,
  "password" varchar(80) NOT NULL,
  "created_at" varchar(80) NOT NULL,
  PRIMARY KEY ("id")
);

CREATE TABLE "location" (
  "id" int NOT NULL AUTO_INCREMENT,
  "email" varchar(80) NOT NULL,
  "latitude" decimal(10,8) NOT NULL DEFAULT '0.00000000',
  "longitude" decimal(11,8) NOT NULL DEFAULT '0.00000000',
  "user_type" varchar(80) NOT NULL,
  "created_at" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  "driver_type" varchar(255) DEFAULT NULL,
  PRIMARY KEY ("id")
);

CREATE TABLE "messages" (
  "id" int NOT NULL AUTO_INCREMENT,
  "email" varchar(255) NOT NULL,
  "receiver_email" varchar(255) NOT NULL,
  "unique_identifier" varchar(255) NOT NULL,
  "message" varchar(255) NOT NULL,
  "created_at" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id")
);
INSERT INTO "messages" ("email", "receiver_email", "unique_identifier", "message", "created_at")
VALUES 
('hiir443@gmail.com', 'Hh@gmail.com', 'ce9ec041-da81-4f70-a475-b4b6cd284c35', 'Yo', '2024-10-30 23:38:56'),
('hiir443@gmail.com', 'Hh@gmail.com', 'ce9ec041-da81-4f70-a475-b4b6cd284c35', 'Yo', '2024-10-30 23:39:03'),
('hiir443@gmail.com', 'Hh@gmail.com', 'ce9ec041-da81-4f70-a475-b4b6cd284c35', 'Ff', '2024-10-30 23:39:08'),
('hiir443@gmail.com', 'Hh@gmail.com', 'ce9ec041-da81-4f70-a475-b4b6cd284c35', 'Yo', '2024-10-30 23:39:51'),
('hiir443@gmail.com', 'Hh@gmail.com', 'ce9ec041-da81-4f70-a475-b4b6cd284c35', 'Yo', '2024-10-30 23:41:35'),
('hiir443@gmail.com', 'Hh@gmail.com', '6e1be35b-db23-4c5b-9a20-6eba3f3d3173', 'Yo', '2024-10-31 00:02:37'),
('Hh@gmail.com', 'hiir443@gmail.com', '6e1be35b-db23-4c5b-9a20-6eba3f3d3173', 'Yo', '2024-10-31 00:06:40'),
('hiir443@gmail.com', 'Hh@gmail.com', '6e1be35b-db23-4c5b-9a20-6eba3f3d3173', 'Yo', '2024-10-31 00:08:18'),
('hiir443@gmail.com', 'Hh@gmail.com', 'e2530d89-78e8-4356-9d5e-4dc76ac2e3b5', 'Yo', '2024-10-31 00:12:03'),
('Hh@gmail.com', 'hiir443@gmail.com', 'e2530d89-78e8-4356-9d5e-4dc76ac2e3b5', 'Hi', '2024-10-31 00:12:33'),
('hiir443@gmail.com', 'Hh@gmail.com', 'e2530d89-78e8-4356-9d5e-4dc76ac2e3b5', 'How r u?', '2024-10-31 00:12:50'),
('Hh@gmail.com', 'hiir443@gmail.com', 'e2530d89-78e8-4356-9d5e-4dc76ac2e3b5', 'Fine', '2024-10-31 00:13:08'),
('hiir443@gmail.com', 'Hh@gmail.com', '4275e06f-90a0-4881-9e3f-74fcb888956c', 'Hey', '2024-10-31 08:38:17'),
('Hh@gmail.com', 'hiir443@gmail.com', '4275e06f-90a0-4881-9e3f-74fcb888956c', 'Hi', '2024-10-31 08:38:25'),
('hiir443@gmail.com', 'Hh@gmail.com', '4275e06f-90a0-4881-9e3f-74fcb888956c', 'Okay good it''s working', '2024-10-31 08:38:37'),
('Hh@gmail.com', 'hiir443@gmail.com', '4275e06f-90a0-4881-9e3f-74fcb888956c', 'Where are you', '2024-10-31 08:39:01'),
('hiir443@gmail.com', 'Hh@gmail.com', '4275e06f-90a0-4881-9e3f-74fcb888956c', 'I''m at elijiji', '2024-10-31 08:39:32'),
('m47865584@gmail.com', 'ww@gmail.com', 'acdbc966-ccf2-4c1f-8546-a105711586ae', 'Hello', '2024-10-31 17:12:28'),
('ww@gmail.com', 'm47865584@gmail.com', 'acdbc966-ccf2-4c1f-8546-a105711586ae', 'Hi', '2024-10-31 17:12:39'),
('jerryvendor980@gmail.com', 'Hh@gmail.com', '126c0ee8-797d-4c07-bff6-d592d999e9be', 'Hi', '2024-10-31 17:37:47');


CREATE TABLE "rides" (
  "id" int NOT NULL AUTO_INCREMENT,
  "email" varchar(80) NOT NULL,
  "driver_email" varchar(80) NOT NULL,
  "ride_id" varchar(100) NOT NULL,
  "created_at" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id")
);

CREATE TABLE "subscriptions" (
  "id" int NOT NULL AUTO_INCREMENT,
  "email" varchar(80) NOT NULL,
  "transaction_id" varchar(100) NOT NULL,
  "reference_id" varchar(100) NOT NULL,
  "months_paid" int NOT NULL,
  "created_at" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  "expires_at" timestamp NULL DEFAULT NULL,
  PRIMARY KEY ("id")
);

INSERT INTO subscriptions (8, chiwendunwoha77@gmail.com, 386b925d-1f25-4cea-b1b9-eee2ad0f46f6, a58228d2-19a1-4eee-87b5-7c0d1a117f28, 1, 2024-12-02 22:54:17, 2025-01-01 22:54:17) VALUES (8, 'chiwendunwoha77@gmail.com', '386b925d-1f25-4cea-b1b9-eee2ad0f46f6', 'a58228d2-19a1-4eee-87b5-7c0d1a117f28', 1, datetime.datetime(2024, 12, 2, 22, 54, 17), datetime.datetime(2025, 1, 1, 22, 54, 17));
INSERT INTO subscriptions (9, Chidiebereokorie77@gmail.com, 2c80e9b4-7b09-474b-853d-0db18fbba712, 7ccb3a33-0d5e-4534-b298-cd8c9d0706a7, 1, 2024-12-04 02:42:47, 2025-01-03 02:42:48) VALUES (9, 'Chidiebereokorie77@gmail.com', '2c80e9b4-7b09-474b-853d-0db18fbba712', '7ccb3a33-0d5e-4534-b298-cd8c9d0706a7', 1, datetime.datetime(2024, 12, 4, 2, 42, 47), datetime.datetime(2025, 1, 3, 2, 42, 48));
CREATE TABLE "user_rides" (
  "id" int NOT NULL AUTO_INCREMENT,
  "email" varchar(80) NOT NULL,
  "driver_email" varchar(80) NOT NULL,
  "ride_id" varchar(100) NOT NULL,
  "created_at" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  "reference_id" varchar(255) NOT NULL,
  "status" varchar(80) NOT NULL DEFAULT 'ongoing',
  PRIMARY KEY ("id")
);

INSERT INTO user_rides (29, Hr@twinkkles.com, chiwendunwoha77@gmail.com, chiwendunwoha77_Hr, 2024-12-02 22:55:47, 6556bb9d-e7b8-4526-9664-f72c665abec3, ongoing) VALUES (29, 'Hr@twinkkles.com', 'chiwendunwoha77@gmail.com', 'chiwendunwoha77_Hr', datetime.datetime(2024, 12, 2, 22, 55, 47), '6556bb9d-e7b8-4526-9664-f72c665abec3', 'ongoing');
INSERT INTO user_rides (30, chiwendunwoha77@gmail.com, chiwendunwoha77@gmail.com, chiwendunwoha77Hr, 2024-12-02 22:56:06, b8d1be92-012c-4e41-adfa-b35236e48e3d, cancelled) VALUES (30, 'chiwendunwoha77@gmail.com', 'chiwendunwoha77@gmail.com', 'chiwendunwoha77Hr', datetime.datetime(2024, 12, 2, 22, 56, 6), 'b8d1be92-012c-4e41-adfa-b35236e48e3d', 'cancelled');
INSERT INTO user_rides (31, bangstech3@gmail.com, Chidiebereokorie77@gmail.com, Chidiebereokorie77bangstech3, 2024-12-04 11:02:53, edf8439e-e068-4187-9235-261d8f316ca7, cancelled) VALUES (31, 'bangstech3@gmail.com', 'Chidiebereokorie77@gmail.com', 'Chidiebereokorie77bangstech3', datetime.datetime(2024, 12, 4, 11, 2, 53), 'edf8439e-e068-4187-9235-261d8f316ca7', 'cancelled');
INSERT INTO user_rides (32, emmanuelhudson355@gmail.com, Chidiebereokorie77@gmail.com, Chidiebereokorie77emmanuelhudson355, 2024-12-05 14:25:43, 2a51baed-a62d-479b-8bba-61382d5c571b, cancelled) VALUES (32, 'emmanuelhudson355@gmail.com', 'Chidiebereokorie77@gmail.com', 'Chidiebereokorie77emmanuelhudson355', datetime.datetime(2024, 12, 5, 14, 25, 43), '2a51baed-a62d-479b-8bba-61382d5c571b', 'cancelled');
CREATE TABLE "userauth" (
  "id" int NOT NULL AUTO_INCREMENT,
  "email" varchar(80) NOT NULL,
  "password" varchar(255) DEFAULT NULL,
  "created_at" timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  "name" varchar(80) NOT NULL,
  "phone_number" varchar(80) NOT NULL,
  "user_type" varchar(80) NOT NULL,
  "balance" int NOT NULL DEFAULT '0',
  "age" int NOT NULL DEFAULT '18',
  "gender" varchar(80) NOT NULL DEFAULT 'Male',
  "driver_type" varchar(255) DEFAULT NULL,
  PRIMARY KEY ("id")
);

INSERT INTO userauth (45, emmanuelhudson355@gmail.com, scrypt:32768:8:1$LCfQvVf8wvMf7RKI$73b1399937aeef6916bf115eca20480d5ee9a869b4814a0c9325bef0d21157bd6a20ae73e2cf72254a903293f77d1a15b35683e551e9787f17e38f83ba91091a, 2024-11-30 19:40:03, Tami Raphael, 07056916222, user, 0, 18, Male, None) VALUES (45, 'emmanuelhudson355@gmail.com', 'scrypt:32768:8:1$LCfQvVf8wvMf7RKI$73b1399937aeef6916bf115eca20480d5ee9a869b4814a0c9325bef0d21157bd6a20ae73e2cf72254a903293f77d1a15b35683e551e9787f17e38f83ba91091a', datetime.datetime(2024, 11, 30, 19, 40, 3), 'Tami Raphael', '07056916222', 'user', 0, 18, 'Male', None);
INSERT INTO userauth (46, task@twinkkles.com, scrypt:32768:8:1$wIVk3iXEjafz8ZVP$dad5bf21d4bd06101c419f71d6904cc5ffcdf4d8f00518f7c8edb00115bbe7336b8a2cc5645f091acab25feadc22c271dd611a9f76a6feca0144b652acecc920, 2024-11-30 19:54:27, Chidi, 08137127672, user, 0, 18, Male, None) VALUES (46, 'task@twinkkles.com', 'scrypt:32768:8:1$wIVk3iXEjafz8ZVP$dad5bf21d4bd06101c419f71d6904cc5ffcdf4d8f00518f7c8edb00115bbe7336b8a2cc5645f091acab25feadc22c271dd611a9f76a6feca0144b652acecc920', datetime.datetime(2024, 11, 30, 19, 54, 27), 'Chidi', '08137127672', 'user', 0, 18, 'Male', None);
INSERT INTO userauth (47, bangstech3@gmail.com, scrypt:32768:8:1$9LbdtMmqo2GAtPPp$eadd196e16127bb34044337ab97f3cb459bc426177cccaab872889545361c6d60a4d1192c0e552b39846013cfccfc0a645d62f51cb6fe112872dd4c1c19b778a, 2024-12-02 18:22:44, Chidiebere Okorie, 09037017453, user, 0, 18, Male, None) VALUES (47, 'bangstech3@gmail.com', 'scrypt:32768:8:1$9LbdtMmqo2GAtPPp$eadd196e16127bb34044337ab97f3cb459bc426177cccaab872889545361c6d60a4d1192c0e552b39846013cfccfc0a645d62f51cb6fe112872dd4c1c19b778a', datetime.datetime(2024, 12, 2, 18, 22, 44), 'Chidiebere Okorie', '09037017453', 'user', 0, 18, 'Male', None);
INSERT INTO userauth (48, Hr@twinkkles.com, scrypt:32768:8:1$aZrQKhc5IrTGDB4E$94f06f5263187334643dd8a65025fa0e4f42b73d03f1a05baee7ba98058792a512997b55f328ebd38c0a1f0c0fde78cb414cd777b108f573c6e8756b90e005fa, 2024-12-02 21:48:49, John thomas, 08137127672, user, 0, 18, Male, None) VALUES (48, 'Hr@twinkkles.com', 'scrypt:32768:8:1$aZrQKhc5IrTGDB4E$94f06f5263187334643dd8a65025fa0e4f42b73d03f1a05baee7ba98058792a512997b55f328ebd38c0a1f0c0fde78cb414cd777b108f573c6e8756b90e005fa', datetime.datetime(2024, 12, 2, 21, 48, 49), 'John thomas', '08137127672', 'user', 0, 18, 'Male', None);
INSERT INTO userauth (49, chiwendunwoha77@gmail.com, scrypt:32768:8:1$6jpQrLhOekIwnzAg$e0f007aaf6cd94f4075da84f37af28d0ec0eeba864d431e6b3d378431a91baf586633a03a3bfa38e45876e10b55da62cf534154295726e7d3f07429482984e23, 2024-12-02 22:46:28, Syb, 07064004829, driver, 0, 28,  Male, None) VALUES (49, 'chiwendunwoha77@gmail.com', 'scrypt:32768:8:1$6jpQrLhOekIwnzAg$e0f007aaf6cd94f4075da84f37af28d0ec0eeba864d431e6b3d378431a91baf586633a03a3bfa38e45876e10b55da62cf534154295726e7d3f07429482984e23', datetime.datetime(2024, 12, 2, 22, 46, 28), 'Syb', '07064004829', 'driver', 0, 28, ' Male', None);
INSERT INTO userauth (50, tomura7772@gmail.com, scrypt:32768:8:1$BLNdJHPqtBRgt1dW$ad1ca30a4161f4be74498a3b2b1665b0092f6476efa5351421929c5d81d5f799db0c627550536f583eda263179d66aafbf40622725d20047e01bfb127eb1d2c7, 2024-12-03 08:50:49, Gomi, 07044831729, user, 0, 18, Male, None) VALUES (50, 'tomura7772@gmail.com', 'scrypt:32768:8:1$BLNdJHPqtBRgt1dW$ad1ca30a4161f4be74498a3b2b1665b0092f6476efa5351421929c5d81d5f799db0c627550536f583eda263179d66aafbf40622725d20047e01bfb127eb1d2c7', datetime.datetime(2024, 12, 3, 8, 50, 49), 'Gomi', '07044831729', 'user', 0, 18, 'Male', None);
INSERT INTO userauth (51, Finance@twinkkles.com, scrypt:32768:8:1$w7Wi4yOHjKtTWnbi$b5f590d7a586a3d12921edb2d56b55f116305189e9e9352efd0a9d697138be4604fa002386138f1016546508d32c13092db1e2706ae2c4d81aba9dfc5bace081, 2024-12-03 20:34:30, Terry, 08137127672, user, 0, 18, Male, None) VALUES (51, 'Finance@twinkkles.com', 'scrypt:32768:8:1$w7Wi4yOHjKtTWnbi$b5f590d7a586a3d12921edb2d56b55f116305189e9e9352efd0a9d697138be4604fa002386138f1016546508d32c13092db1e2706ae2c4d81aba9dfc5bace081', datetime.datetime(2024, 12, 3, 20, 34, 30), 'Terry', '08137127672', 'user', 0, 18, 'Male', None);
INSERT INTO userauth (52, droptwinkkles@gmail.com, scrypt:32768:8:1$hwgHfY8vpPSN585y$b93e15b6e6f0a3d20a02999fa1d10181adee6dcd4a5d0b6a216419da7394df7d60bb26e429bbf93ce16f07fe9ca254fdc6ac5afad5b0b01b6ff1b07aaed6e060, 2024-12-04 01:27:21, Tomura Shigaraki, 08017232182, driver, 0, 21, Male, None) VALUES (52, 'droptwinkkles@gmail.com', 'scrypt:32768:8:1$hwgHfY8vpPSN585y$b93e15b6e6f0a3d20a02999fa1d10181adee6dcd4a5d0b6a216419da7394df7d60bb26e429bbf93ce16f07fe9ca254fdc6ac5afad5b0b01b6ff1b07aaed6e060', datetime.datetime(2024, 12, 4, 1, 27, 21), 'Tomura Shigaraki', '08017232182', 'driver', 0, 21, 'Male', None);
INSERT INTO userauth (53, Chidiebereokorie77@gmail.com, scrypt:32768:8:1$jofowcMa3ZmkifMg$5aa4cb076ec280eec9b2ab6ca9b3664395cf1be8bf7a974d6db19b7fc293d51e15488687b1500f2da97155097a7231a5bc6eebd732e7dc03bf3883e4fa566f82, 2024-12-04 02:29:44, Emmanuel , 08067685196, driver, 0, 21, Male, None) VALUES (53, 'Chidiebereokorie77@gmail.com', 'scrypt:32768:8:1$jofowcMa3ZmkifMg$5aa4cb076ec280eec9b2ab6ca9b3664395cf1be8bf7a974d6db19b7fc293d51e15488687b1500f2da97155097a7231a5bc6eebd732e7dc03bf3883e4fa566f82', datetime.datetime(2024, 12, 4, 2, 29, 44), 'Emmanuel ', '08067685196', 'driver', 0, 21, 'Male', None);
CREATE TABLE "verificationdetails" (
  "id" int NOT NULL AUTO_INCREMENT,
  "email" varchar(80) NOT NULL,
  "phone_number" varchar(255) NOT NULL,
  "gender" varchar(80) NOT NULL DEFAULT 'Male',
  "plate_number" varchar(80) NOT NULL,
  "driver_photo" varchar(255) DEFAULT NULL,
  "license_photo" varchar(255) DEFAULT NULL,
  "car_photo" varchar(255) DEFAULT NULL,
  "plate_photo" varchar(255) DEFAULT NULL,
  "car_color" varchar(80) DEFAULT NULL,
  "driver_with_car_photo" varchar(255) DEFAULT NULL,
  "status" varchar(80) NOT NULL DEFAULT 'pending',
  PRIMARY KEY ("id")
);

INSERT INTO verificationdetails (11, domole235@gmail.com, 08071273078, Male, ABC-1234, None, None, None, None, , None, pending) VALUES (11, 'domole235@gmail.com', '08071273078', 'Male', 'ABC-1234', None, None, None, None, '', None, 'pending');
INSERT INTO verificationdetails (12, chiwendunwoha77@gmail.com, 08071273078, Male, ABC-1234cccvv, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733179629/vmp6a5uvj9dx5vnnwuyj.jpg, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733179630/ivcjqcs77hhjqk8ywifa.jpg, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733179629/rdukm4togheg3t6ci3xk.jpg, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733179631/ukpfqwu07s4qdbpc0xa5.jpg, Gols, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733179634/u7fljsilyoicm2wyiqxw.jpg, success) VALUES (12, 'chiwendunwoha77@gmail.com', '08071273078', 'Male', 'ABC-1234cccvv', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733179629/vmp6a5uvj9dx5vnnwuyj.jpg', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733179630/ivcjqcs77hhjqk8ywifa.jpg', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733179629/rdukm4togheg3t6ci3xk.jpg', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733179631/ukpfqwu07s4qdbpc0xa5.jpg', 'Gols', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733179634/u7fljsilyoicm2wyiqxw.jpg', 'success');
INSERT INTO verificationdetails (13, droptwinkkles@gmail.com, 08071273078, Male, ABC-1234, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733275773/htztdfgfm1jaki0dqhlx.jpg, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733275773/tosqzeksiahxr7lc1vbz.jpg, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733275772/l2mzys0b8zvp8krggpmz.jpg, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733275774/hj0j1aocheolm2zl7eab.jpg, Red, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733275774/odk2w1qmat73rw0etyl0.jpg, success) VALUES (13, 'droptwinkkles@gmail.com', '08071273078', 'Male', 'ABC-1234', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733275773/htztdfgfm1jaki0dqhlx.jpg', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733275773/tosqzeksiahxr7lc1vbz.jpg', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733275772/l2mzys0b8zvp8krggpmz.jpg', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733275774/hj0j1aocheolm2zl7eab.jpg', 'Red', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733275774/odk2w1qmat73rw0etyl0.jpg', 'success');
INSERT INTO verificationdetails (14, Chidiebereokorie77@gmail.com, 08071273078, Male, 32578, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733279446/j8o0n6cunnmjbas2qywl.jpg, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733279447/nmdb0oiyb10b8imas2ad.jpg, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733279445/akcgioz1vmwt9kg2wiqd.jpg, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733279448/pitd7vppu6lfldjycfjn.jpg, Black, https://res.cloudinary.com/dqmhfzfis/image/upload/v1733279448/hr0o7ydrbgf4jrmx4ahy.jpg, success) VALUES (14, 'Chidiebereokorie77@gmail.com', '08071273078', 'Male', '32578', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733279446/j8o0n6cunnmjbas2qywl.jpg', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733279447/nmdb0oiyb10b8imas2ad.jpg', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733279445/akcgioz1vmwt9kg2wiqd.jpg', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733279448/pitd7vppu6lfldjycfjn.jpg', 'Black', 'https://res.cloudinary.com/dqmhfzfis/image/upload/v1733279448/hr0o7ydrbgf4jrmx4ahy.jpg', 'success');
