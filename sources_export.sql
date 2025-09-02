PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE sources (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	url VARCHAR(500) NOT NULL, 
	source_type VARCHAR(50) NOT NULL, 
	description TEXT, 
	thumbnail_url VARCHAR(500), 
	is_active BOOLEAN, 
	last_updated DATETIME, 
	update_interval INTEGER, 
	source_metadata JSON, 
	PRIMARY KEY (id)
);
INSERT INTO sources VALUES(1,'Platformer (Casey Newton)','https://www.platformer.news/feed','media','Magazine source: Platformer (Casey Newton) (media)',NULL,1,'2025-09-02 05:05:50.608515',3600,NULL);
INSERT INTO sources VALUES(2,'The Information','https://www.theinformation.com/feed','media','Magazine source: The Information (media)',NULL,1,'2025-09-02 05:05:50.997317',3600,NULL);
INSERT INTO sources VALUES(3,'Nieman Lab','http://www.niemanlab.org/feed/','media','Magazine source: Nieman Lab (media)',NULL,1,'2025-09-02 05:05:51.526082',3600,NULL);
INSERT INTO sources VALUES(4,'Poynter','https://www.poynter.org/feed/','media','Magazine source: Poynter (media)',NULL,1,'2025-09-02 05:05:52.477386',3600,NULL);
INSERT INTO sources VALUES(5,'Columbia Journalism Review','https://www.cjr.org/feed.rss','media','Magazine source: Columbia Journalism Review (media)',NULL,1,'2025-09-02 05:05:53.462764',3600,NULL);
INSERT INTO sources VALUES(6,'Digiday','https://digiday.com/feed/','media','Magazine source: Digiday (media)',NULL,1,'2025-09-02 05:05:56.535174',3600,NULL);
INSERT INTO sources VALUES(7,'AdAge','https://adage.com/rss.xml','media','Magazine source: AdAge (media)',NULL,1,'2025-09-02 05:06:02.556657',3600,NULL);
INSERT INTO sources VALUES(8,'Marketing Land','https://marketingland.com/feed','media','Magazine source: Marketing Land (media)',NULL,1,'2025-09-02 05:06:05.449066',3600,NULL);
INSERT INTO sources VALUES(9,'TechMeme','https://www.techmeme.com/feed.xml','media','Magazine source: TechMeme (media)',NULL,1,'2025-09-02 05:06:10.851416',3600,NULL);
INSERT INTO sources VALUES(10,'Axios Media','https://www.axios.com/media/feed/','media','Magazine source: Axios Media (media)',NULL,1,'2025-09-02 05:06:11.399013',3600,NULL);
INSERT INTO sources VALUES(11,'The Wrap','https://www.thewrap.com/feed/','media','Magazine source: The Wrap (media)',NULL,1,'2025-09-02 05:06:14.409973',3600,NULL);
INSERT INTO sources VALUES(12,'Variety','https://variety.com/feed/','media','Magazine source: Variety (media)',NULL,1,'2025-09-02 05:06:18.885632',3600,NULL);
INSERT INTO sources VALUES(13,'Hollywood Reporter','https://www.hollywoodreporter.com/feed/','media','Magazine source: Hollywood Reporter (media)',NULL,1,'2025-09-02 05:06:24.842227',3600,NULL);
INSERT INTO sources VALUES(14,'Media Post','https://www.mediapost.com/rss/','media','Magazine source: Media Post (media)',NULL,1,'2025-09-02 05:06:27.161034',3600,NULL);
INSERT INTO sources VALUES(15,'Press Gazette','https://pressgazette.co.uk/feed/','media','Magazine source: Press Gazette (media)',NULL,1,'2025-09-02 05:06:31.267322',3600,NULL);
INSERT INTO sources VALUES(16,'Creator Economy Report','https://creatoreconomy.so/feed/','creator','Magazine source: Creator Economy Report (creator)',NULL,1,'2025-09-02 05:06:33.433511',3600,NULL);
INSERT INTO sources VALUES(17,'ConvertKit Creator Economy','https://convertkit.com/creator-economy/feed','creator','Magazine source: ConvertKit Creator Economy (creator)',NULL,1,'2025-09-02 05:06:35.782137',3600,NULL);
INSERT INTO sources VALUES(18,'The Tilt','https://www.thetilt.com/rss','creator','Magazine source: The Tilt (creator)',NULL,1,'2025-09-02 05:06:40.893562',3600,NULL);
INSERT INTO sources VALUES(19,'Not Boring by Packy McCormick','https://www.notboring.co/feed','creator','Magazine source: Not Boring by Packy McCormick (creator)',NULL,1,'2025-09-02 05:06:43.616450',3600,NULL);
INSERT INTO sources VALUES(20,'Morning Brew Creator Economy','https://www.morningbrew.com/creator-economy/feed','creator','Magazine source: Morning Brew Creator Economy (creator)',NULL,1,'2025-09-02 05:06:44.076939',3600,NULL);
INSERT INTO sources VALUES(21,'YouTube Creator Blog','https://youtube-creators.googleblog.com/feeds/posts/default','creator','Magazine source: YouTube Creator Blog (creator)',NULL,1,'2025-09-02 05:06:49.124122',3600,NULL);
INSERT INTO sources VALUES(22,'TubeBuddy Blog','https://www.tubebuddy.com/blog/feed','creator','Magazine source: TubeBuddy Blog (creator)',NULL,1,'2025-09-02 05:06:52.861456',3600,NULL);
INSERT INTO sources VALUES(23,'VidIQ Blog','https://vidiq.com/blog/feed/','creator','Magazine source: VidIQ Blog (creator)',NULL,1,'2025-09-02 05:06:54.215523',3600,NULL);
INSERT INTO sources VALUES(24,'Think Media','https://www.thinkmedia.com/feed/','creator','Magazine source: Think Media (creator)',NULL,1,'2025-09-02 05:06:59.455218',3600,NULL);
INSERT INTO sources VALUES(25,'The Ken Creator','https://the-ken.com/category/creator-economy/feed/','creator','Magazine source: The Ken Creator (creator)',NULL,1,'2025-09-02 05:07:02.567780',3600,NULL);
INSERT INTO sources VALUES(26,'Inc42 Creator Economy','https://inc42.com/buzz/creator-economy/feed/','creator','Magazine source: Inc42 Creator Economy (creator)',NULL,1,'2025-09-02 05:07:06.161422',3600,NULL);
INSERT INTO sources VALUES(27,'YourStory Creator','https://yourstory.com/category/creator-economy/feed','creator','Magazine source: YourStory Creator (creator)',NULL,1,'2025-09-02 05:07:06.466394',3600,NULL);
INSERT INTO sources VALUES(28,'Economic Times Creator','https://economictimes.indiatimes.com/topic/creator-economy/rss','creator','Magazine source: Economic Times Creator (creator)',NULL,1,'2025-09-02 05:07:09.285388',3600,NULL);
INSERT INTO sources VALUES(29,'Reddit Creator Economy','http://www.reddit.com/r/creatoreconomy/.rss','creator','Magazine source: Reddit Creator Economy (creator)',NULL,1,'2025-09-02 05:07:10.028693',3600,NULL);
INSERT INTO sources VALUES(30,'Reddit YouTube Creators','http://www.reddit.com/r/PartneredYoutube/.rss','creator','Magazine source: Reddit YouTube Creators (creator)',NULL,1,'2025-09-02 05:07:10.812690',3600,NULL);
INSERT INTO sources VALUES(31,'Reddit Content Creation','http://www.reddit.com/r/ContentCreation/.rss','creator','Magazine source: Reddit Content Creation (creator)',NULL,1,'2025-09-02 05:07:11.420737',3600,NULL);
INSERT INTO sources VALUES(32,'Reddit Creator Support','http://www.reddit.com/r/CreatorsAdvice/.rss','creator','Magazine source: Reddit Creator Support (creator)',NULL,1,'2025-09-02 05:07:12.014360',3600,NULL);
INSERT INTO sources VALUES(33,'Stratechery','https://stratechery.com/feed/','business_models','Magazine source: Stratechery (business_models)',NULL,1,'2025-09-02 05:07:14.838333',3600,NULL);
INSERT INTO sources VALUES(34,'The Rebooting','https://www.therebooting.com/feed/','business_models','Magazine source: The Rebooting (business_models)',NULL,1,'2025-09-02 05:07:16.561604',3600,NULL);
INSERT INTO sources VALUES(35,'Whats New in Publishing','https://whatsnewinpublishing.com/feed/','business_models','Magazine source: Whats New in Publishing (business_models)',NULL,1,'2025-09-02 05:07:34.034836',3600,NULL);
INSERT INTO sources VALUES(36,'Nieman Lab Business','http://www.niemanlab.org/feed/','business_models','Magazine source: Nieman Lab Business (business_models)',NULL,1,'2025-09-02 05:07:34.580466',3600,NULL);
INSERT INTO sources VALUES(37,'Media Voices','https://www.mediavoices.org/feed/','business_models','Magazine source: Media Voices (business_models)',NULL,1,'2025-09-02 05:07:34.669802',3600,NULL);
INSERT INTO sources VALUES(38,'Pugpig','https://pugpig.com/feed/','business_models','Magazine source: Pugpig (business_models)',NULL,1,'2025-09-02 05:07:35.531958',3600,NULL);
INSERT INTO sources VALUES(39,'WAN-IFRA','https://wan-ifra.org/feed/','business_models','Magazine source: WAN-IFRA (business_models)',NULL,1,'2025-09-02 05:07:40.016461',3600,NULL);
INSERT INTO sources VALUES(40,'a16z Media','https://a16z.com/feed/','business_models','Magazine source: a16z Media (business_models)',NULL,1,'2025-09-02 05:07:43.297448',3600,NULL);
INSERT INTO sources VALUES(41,'First Round Review','https://review.firstround.com/feed','business_models','Magazine source: First Round Review (business_models)',NULL,1,'2025-09-02 05:07:46.939307',3600,NULL);
INSERT INTO sources VALUES(42,'Bessemer VP Media','https://www.bvp.com/feed','business_models','Magazine source: Bessemer VP Media (business_models)',NULL,1,'2025-09-02 05:07:49.407555',3600,NULL);
INSERT INTO sources VALUES(43,'Lightspeed Venture','https://lsvp.com/feed/','business_models','Magazine source: Lightspeed Venture (business_models)',NULL,1,'2025-09-02 05:07:50.236213',3600,NULL);
INSERT INTO sources VALUES(44,'Sequoia Capital','https://www.sequoiacap.com/feed/','business_models','Magazine source: Sequoia Capital (business_models)',NULL,1,'2025-09-02 05:07:52.821918',3600,NULL);
INSERT INTO sources VALUES(45,'Harvard Business Review Media','http://feeds.hbr.org/harvardbusiness','business_models','Magazine source: Harvard Business Review Media (business_models)',NULL,1,'2025-09-02 05:07:57.191358',3600,NULL);
INSERT INTO sources VALUES(46,'McKinsey Media','https://www.mckinsey.com/capabilities/mckinsey-digital/our-insights/rss','business_models','Magazine source: McKinsey Media (business_models)',NULL,1,'2025-09-02 05:08:02.520844',3600,NULL);
INSERT INTO sources VALUES(47,'PwC Media Outlook','https://www.pwc.com/gx/en/entertainment-media/outlook/feed.xml','business_models','Magazine source: PwC Media Outlook (business_models)',NULL,1,'2025-09-02 05:08:04.953768',3600,NULL);
INSERT INTO sources VALUES(48,'Deloitte Media','https://www2.deloitte.com/us/en/industries/technology-media-telecommunications/feed.xml','business_models','Magazine source: Deloitte Media (business_models)',NULL,1,'2025-09-02 05:08:05.791761',3600,NULL);
INSERT INTO sources VALUES(49,'All In Podcast','https://feeds.simplecast.com/JCLotU5d','podcasts','Magazine source: All In Podcast (podcasts)',NULL,1,'2025-09-02 05:08:07.456119',3600,NULL);
INSERT INTO sources VALUES(50,'The Tim Ferriss Show','http://feeds.feedburner.com/thetimferrissshow','podcasts','Magazine source: The Tim Ferriss Show (podcasts)',NULL,1,'2025-09-02 05:08:12.924941',3600,NULL);
INSERT INTO sources VALUES(51,'How I Built This','https://feeds.npr.org/510313/podcast.xml','podcasts','Magazine source: How I Built This (podcasts)',NULL,1,'2025-09-02 05:08:20.702994',3600,NULL);
INSERT INTO sources VALUES(52,'Masters of Scale','https://feeds.megaphone.fm/mastersofscale','podcasts','Magazine source: Masters of Scale (podcasts)',NULL,1,'2025-09-02 05:08:22.009027',3600,NULL);
INSERT INTO sources VALUES(53,'The GaryVee Audio Experience','http://feeds.feedburner.com/garyvaynerchuk','podcasts','Magazine source: The GaryVee Audio Experience (podcasts)',NULL,1,'2025-09-02 05:08:23.152158',3600,NULL);
INSERT INTO sources VALUES(54,'Smart Passive Income','http://feeds.feedburner.com/smartpassiveincome','podcasts','Magazine source: Smart Passive Income (podcasts)',NULL,1,'2025-09-02 05:08:24.703926',3600,NULL);
INSERT INTO sources VALUES(55,'Entrepreneur on Fire','http://feeds.feedburner.com/eofire','podcasts','Magazine source: Entrepreneur on Fire (podcasts)',NULL,1,'2025-09-02 05:08:25.867244',3600,NULL);
INSERT INTO sources VALUES(56,'The Creator Economy Show','https://feeds.buzzsprout.com/1404486.rss','podcasts','Magazine source: The Creator Economy Show (podcasts)',NULL,1,'2025-09-02 05:08:26.452015',3600,NULL);
INSERT INTO sources VALUES(57,'Recode Decode','https://feeds.megaphone.fm/recode-decode','podcasts','Magazine source: Recode Decode (podcasts)',NULL,1,'2025-09-02 05:08:27.385330',3600,NULL);
INSERT INTO sources VALUES(58,'The Vergecast','https://feeds.megaphone.fm/vergecast','podcasts','Magazine source: The Vergecast (podcasts)',NULL,1,'2025-09-02 05:08:28.323494',3600,NULL);
INSERT INTO sources VALUES(59,'Pivot','https://feeds.megaphone.fm/pivot','podcasts','Magazine source: Pivot (podcasts)',NULL,1,'2025-09-02 05:08:28.781433',3600,NULL);
INSERT INTO sources VALUES(60,'Land of the Giants','https://feeds.megaphone.fm/land-of-the-giants','podcasts','Magazine source: Land of the Giants (podcasts)',NULL,1,'2025-09-02 05:08:29.918393',3600,NULL);
INSERT INTO sources VALUES(61,'Reply All','https://feeds.gimletmedia.com/reply-all','podcasts','Magazine source: Reply All (podcasts)',NULL,1,'2025-09-02 05:08:32.077048',3600,NULL);
INSERT INTO sources VALUES(62,'StartUp Podcast','https://feeds.gimletmedia.com/hearstartup','podcasts','Magazine source: StartUp Podcast (podcasts)',NULL,1,'2025-09-02 05:08:32.726420',3600,NULL);
INSERT INTO sources VALUES(63,'The Seen and the Unseen','https://feeds.transistor.fm/the-seen-and-the-unseen','podcasts','Magazine source: The Seen and the Unseen (podcasts)',NULL,1,'2025-09-02 05:08:34.410429',3600,NULL);
INSERT INTO sources VALUES(64,'IVM Podcast','https://ivmpodcasts.com/feed/podcast/','podcasts','Magazine source: IVM Podcast (podcasts)',NULL,1,'2025-09-02 05:08:35.514091',3600,NULL);
INSERT INTO sources VALUES(65,'The Desi VC','https://feeds.soundcloud.com/users/soundcloud:users:394895517/sounds.rss','podcasts','Magazine source: The Desi VC (podcasts)',NULL,1,'2025-09-02 05:08:37.462089',3600,NULL);
INSERT INTO sources VALUES(66,'Boston Consulting Group','https://www.bcg.com/rss','business_models','Enhanced RSS feed for Boston Consulting Group',NULL,1,'2025-09-02 05:08:39.496019',3600,NULL);
INSERT INTO sources VALUES(67,'Bain & Company','https://www.bain.com/rss/','business_models','Enhanced RSS feed for Bain & Company',NULL,1,'2025-09-02 05:08:41.436625',3600,NULL);
INSERT INTO sources VALUES(68,'TechCrunch Media','https://techcrunch.com/category/media-entertainment/feed/','media','Enhanced RSS feed for TechCrunch Media',NULL,1,'2025-09-02 05:08:44.752796',3600,NULL);
INSERT INTO sources VALUES(69,'Bloomberg Media','https://www.bloomberg.com/feeds/podcasts/media.xml','media','Enhanced RSS feed for Bloomberg Media',NULL,1,'2025-09-02 05:08:50.032739',3600,NULL);
INSERT INTO sources VALUES(70,'Reuters Media & Tech','https://feeds.reuters.com/reuters/technologyNews','media','Enhanced RSS feed for Reuters Media & Tech',NULL,1,'2025-09-02 05:08:50.203105',3600,NULL);
INSERT INTO sources VALUES(71,'Creator Economy Co','https://creatoreconomy.so/feed','creator','Enhanced RSS feed for Creator Economy Co',NULL,1,'2025-09-02 05:08:50.622190',3600,NULL);
INSERT INTO sources VALUES(72,'Passion Economy','https://li.substack.com/feed','creator','Enhanced RSS feed for Passion Economy',NULL,1,'2025-09-02 05:08:50.625717',3600,NULL);
INSERT INTO sources VALUES(73,'Invest Like the Best','https://feeds.simplecast.com/BqbsxVfO','podcasts','Enhanced RSS feed for Invest Like the Best',NULL,1,'2025-09-02 05:08:51.620194',3600,NULL);
INSERT INTO sources VALUES(74,'Acquired Podcast','https://feeds.simplecast.com/WOeILCLy','podcasts','Enhanced RSS feed for Acquired Podcast',NULL,1,'2025-09-02 05:08:52.481430',3600,NULL);
COMMIT;
