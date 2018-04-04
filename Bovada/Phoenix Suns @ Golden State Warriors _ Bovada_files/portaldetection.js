var detectDone = detectDone || false;

/*
	Detects the user's current device, and inserts a device-dependent image link into the given element.
	Clicking the link opens the pre-chat questionnaire using parameters.
	portalId: Guid of the portal to use.
	spantag: Id of the element that will contain the image link.
	introtext: Text that appears below the image link.
	providername: Text that appears after introtext.
	devicetype: Optional number that indicates the preferred device. If specified, device-detection logic is skipped.
		0=portal default, 1=mobile, 2=table, 3=desktop
*/
function DetectDevice(portalId, spantag, introtext, providername, devicetype) {

    if (detectDone == true)
		return
    detectDone = true;

	if (typeof JSON != "object") {
		JSON = {
			parse: jsonParse
		};
	}

	var bopennew = false;
	var urlfront = ""
	var url = "";
	var openbuttonurl = "";
	var closedbuttonurl = "";
	var buttonworkerurl = "";

	var hostname = "";
	var usesecureconn = false;
	var portalport = 0;
	var portallist = "";
	var stylelist = "";
	var imagelanguage = "";
	var openimagesrc = "";
	var closeimagesrc = "";
	var newwindowresize = false;
	var newwindowwidth = "";
	var newwindowheight = "";
	var linktitle = "";
	var tabtext = null;

	var defaultStyle = "";
	var defaultQuestionnaire = "";

	// detect the browser device type if devicetype not specified
	if (devicetype == undefined) {
		if (DetectAndroidPhone() || DetectIphoneOrIpod() || DetectWindowsPhone7()) {
			devicetype = 1; //"mobile";
		} else if (DetectIpad() || DetectAndroidTablet()) {
			devicetype = 2; //"tablet";
		} else if (DetectDesktop()) {
			devicetype = 3; //"desktop";
		} else {
			devicetype = 0; //"default";
		}
	}

	//get portal information from page (this will be needed even if there is an in progress chat for a different portal)
	var currentPortal = MoxieGetPortalSettings(portalId, devicetype);
	var desiredPortal = currentPortal;
	urlfront = MoxieGenerateUrlFront(desiredPortal);
    var pageurl = MoxieGenerateQuestionnaireUrl(desiredPortal, urlfront);
	url = pageurl;

	//if chat is in progress, check to if it is for a different portal, and if so, generate the proper url for it
	var sessionStorageAvail = supports_html5_storage();

    var chatInProgress = sessionStorageAvail && MoxieFlyout.storage.getItem("MoxieFlyout.chatInProgress");
    var flyoutOpen = sessionStorageAvail && chatInProgress > 0 && parseBoolean(MoxieFlyout.storage.getItem("MoxieFlyout.isOpen"));
	if (chatInProgress || flyoutOpen) {
        var activePortalID = MoxieFlyout.storage.getItem("MoxieFlyout.portal");
		if (activePortalID && activePortalID != portalId) {
			portalId = activePortalID;
			desiredPortal = MoxieGetPortalSettings(portalId, devicetype);
			urlfront = MoxieGenerateUrlFront(desiredPortal);
			url = MoxieGenerateQuestionnaireUrl(desiredPortal, urlfront);
		}
        url = MoxieFlyout.storage.getItem("MoxieFlyout.content") || url;
        if (chatInProgress > 0) {
            tabtext = MoxieFlyout.storage.getItem("MoxieFlyout.tabText");
		} else {
            MoxieFlyout.storage.removeItem("MoxieFlyout.tabText");
		}
    } else if (sessionStorageAvail) {
        MoxieFlyout.storage.removeItem("MoxieFlyout.isOpen");
	}
	
	bopennew = desiredPortal.bopennew;
	hostname = desiredPortal.hostname;
	usesecureconn = desiredPortal.usesecureconn;
	portalport = desiredPortal.portalport;
	stylelist = desiredPortal.style;
	imagelanguage = desiredPortal.imagelanguage;
	openimagesrc = desiredPortal.openimagesrc;
	closeimagesrc = desiredPortal.closeimagesrc;
	newwindowresize = desiredPortal.newwindowresize;
	newwindowwidth = desiredPortal.newwindowwidth;
	newwindowheight = desiredPortal.newwindowheight;
	linktitle = desiredPortal.linktitle;

	var selectedStyle = desiredPortal.selectedStyle;
	var selectedQuestionnaire = desiredPortal.selectedQuestionnaire;
	var selectedDevice = desiredPortal.selectedDevice;
	var defaultStyle = desiredPortal.defaultStyle;
	var defaultQuestionnaire = desiredPortal.defaultQuestionnaire;
	var defaultDevice = desiredPortal.defaultDevice;

    if (desiredPortal.tabOrButton == "button") {

		if (!spantag)
			return false;

		buttonworkerurl = urlfront + "/netagent/client/invites/chatimage.aspx?style=" + escape(stylelist) +
			"&questid=" + escape(selectedQuestionnaire) + "&portid=" + escape(selectedStyle) +
			"&imagelanguage=" + escape(imagelanguage);

		if (stylelist == "style0") {
			buttonworkerurl += "&customopenimage=" + escape(openimagesrc);
			buttonworkerurl += "&customcloseimage=" + escape(closeimagesrc);
		}

		var linkcreator = "";

		if (bopennew == true) {
			var resizableVal = newwindowresize ? "yes" : "no";

			linkcreator += "<a href = \"javascript:void(0)\" onclick=\"javascript:window.open('" + url + "&nareferer=' + escape(document.location) " +
				",'_blank','resizable=" + resizableVal + ",width=" + newwindowwidth + ",height=" + newwindowheight + ",scrollbars=yes'); return false;\">";

			linkcreator += "<img src=\"" + buttonworkerurl + "\" border=\"0\" alt=\"" + linktitle + "\"></a>";
		} else {
			linkcreator += "<a href = \"" + url + "\">" +
					"<img src=\"" + buttonworkerurl + "\" border=\"0\" alt=\"" + linktitle + "\"></a>";
		}
		if (!selectedDevice.hidebranding) {
			linkcreator += "\r\n<br><a target=\"_blank\" href=\"https://www.gomoxie.com\" style=\"text-decoration:none\">";
			linkcreator += "<span style=\"margin-left: 35px; font-size: 10px; font-family: Arial, Helvetica, sans-serif\">";
			linkcreator += introtext + " <font color=\"#4d82bb\">" + providername + "</font></span></a>"
		}
		if (document.getElementById(spantag)) {
			document.getElementById(spantag).innerHTML = linkcreator;
		}
	} else if (desiredPortal.tabOrButton == "tab") {

        var objTransform = document.createElement('p');
        
        if (!((objTransform.style['transform'] === undefined) && (objTransform.style['-ms-transform'] === undefined)
		&& (objTransform.style['-webkit-transform'] === undefined) && (objTransform.style['-moz-transform'] === undefined)
		&& (objTransform.style['-o-transform'] === undefined))) { // Browser does not support rotation. Do not show tab.        
			var side = MoxieFlyout.RIGHT;
            switch (desiredPortal.tabLocation) {
				case 't': side = MoxieFlyout.TOP; break;
				case 'b': side = MoxieFlyout.BOTTOM; break;
				case 'l': side = MoxieFlyout.LEFT; break;
				case 'r': side = MoxieFlyout.RIGHT; break;
			}

			var open = false;
			var fullScreen = (devicetype == 1); // fullscreen if device is phone
			if (sessionStorageAvail) {
				url = url + "&flyout=1";
				url = MoxieFlyout.addQueryStringToUrl(url, MoxieFlyout.queryStringType.FullScreen, function () { return fullScreen });

				pageurl = pageurl + "&flyout=1";
				pageurl = MoxieFlyout.addQueryStringToUrl(pageurl, MoxieFlyout.queryStringType.FullScreen, function () { return fullScreen });

				// Determine whether we're resuming a suspended session
				var suspendId = MoxieFlyout.getCookie("SUSPENDID");
				var sessionId = MoxieFlyout.getCookie("SESSIONID");
				var resumingSession = (suspendId && suspendId.length > 0) && (sessionId && sessionId.length > 0);
				if (resumingSession) {
					// Resumed session will cause flyout to open and auto-login from questionnaire
					open = true;
					chatInProgress = true;
				} else {
                    if (MoxieFlyout.storage.getItem("MoxieFlyout.portal") == portalId) {
						//we are making a flyout for the same portal as the last page
						open = flyoutOpen;
					}
				}
			} else {
				// Force flyout to load alternate html
				url = "ERROR";
			}
			var serverURL = urlfront + "/netagent/";
			if (!tabtext) {
				tabtext = decodeURIComponent(selectedDevice.tabText);
			}

			MoxieFlyout.init({
				portalID: portalId,
				style: selectedStyle,
				questionnaire: selectedQuestionnaire,
				flySide: side,
				sideOffset: desiredPortal.tabSideOffset,
				tabColor: selectedDevice.tabBgColor,
				tabText: tabtext,
				tabTextColor: selectedDevice.tabTextColor,
				flyWidth: desiredPortal.newwindowwidth + "px",
				flyHeight: desiredPortal.newwindowheight + "px",
				isFullscreen: fullScreen,
				flyBackColor: selectedDevice.flyOutBgColor,
				flyTitleColor: selectedDevice.titleBgColor,
				flyTitleTextColor: selectedDevice.titleTextColor,
				flyBtnColor: selectedDevice.titleBgColor,
				fontTab: selectedDevice.tabFont,
				fontTitle: selectedDevice.tabFont,
				startOpen: open,
				serverURL: serverURL,
				portalURL: pageurl,
				currentPagePortalId: currentPortal.portalid,
				currentPagePortalStyle: currentPortal.selectedStyle,
				currentPageQuestionnaire: currentPortal.selectedQuestionnaire,
				deviceType: devicetype
			});

			MoxieFlyout.setFlyoutBtn({
				id: "MoxieFlyoutBtn1",
				text: hTMLEncode(decodeURIComponent(selectedDevice.hideText)),
				accessKey: "h",
				title: hTMLEncode(decodeURIComponent(selectedDevice.hideText))
			});

            if (url) {
                if (open || chatInProgress > 0) {
					MoxieFlyout.setFlyoutContent(url);
				} else {
					MoxieFlyout.setFlyoutContentUponOpen(url);
				}
			}
		}
	}
	var flyoutHolderRef = document.getElementById("MoxieFlyoutHolder");
	if (flyoutHolderRef) {
		flyoutHolderRef.style.display='block';
	}
}

function MoxieGetPortalSettings(portalid, devicetype) {
	var desiredPortal = null;
	var defaultStyle = null;
	var defaultQuestionnaire = null;
	var defaultDevice = null;
	var selectedStyle = null;
	var selectedQuestionnaire = null;
	var selectedDevice = null;
	var foundDevice = false;

	for (var i = 0; i < json.length; i++) {
		// if this is the desired portalid
		if (json[i].portalid == portalid) {
			desiredPortal = json[i];
			break;
		}
	}

	// determine if we have entry for detected browser device type
	for (var i = 0; i < desiredPortal.devicedetectionlist.length; i++) {// desiredPortal.devicedetectionlist.length
		var dl = desiredPortal.devicedetectionlist[i];
		if (dl.devicetype == 0) {
			defaultStyle = dl.styleid;
			defaultQuestionnaire = dl.questid;
			defaultDevice = dl;
		} else if (dl.devicetype == devicetype) {
			selectedStyle = dl.styleid;
			selectedQuestionnaire = dl.questid;
			selectedDevice = dl;
			foundDevice = true;
			break;
		}
	}

	// default style and questionnaire apply if detected device type does not match entries for this portal.
	if (foundDevice == false) {
		selectedStyle = defaultStyle;
		selectedQuestionnaire = defaultQuestionnaire;
		selectedDevice = defaultDevice;
		}
		
	desiredPortal.selectedStyle = selectedStyle;
	desiredPortal.selectedQuestionnaire = selectedQuestionnaire;
	desiredPortal.selectedDevice = selectedDevice;
	desiredPortal.defaultStyle = defaultStyle;
	desiredPortal.defaultQuestionnaire = defaultQuestionnaire;
	desiredPortal.defaultDevice = defaultDevice;

	return desiredPortal;
	}
	
function MoxieGenerateUrlFront(desiredPortal) {
    urlfront = (desiredPortal.usesecureconn ? "https://" : "https://") + desiredPortal.hostname;
    urlfront += (desiredPortal.usesecureconn && desiredPortal.portalport != 443 || !desiredPortal.usesecureconn && desiredPortal.portalport != 80) ? (":" + desiredPortal.portalport) : "";
    return urlfront;
}

function MoxieGenerateQuestionnaireUrl(desiredPortal, urlfront) {
    url = urlfront + "/netagent/cimlogin.aspx?questid=" + desiredPortal.selectedQuestionnaire + "&portid=" + desiredPortal.selectedStyle;
    url += "&defaultStyleId=" + escape(desiredPortal.defaultStyle);
    return url;
}

function supports_html5_storage() {
  try {
		// Return true if sessionStorage exists and is writeable
		if ('sessionStorage' in window && window['sessionStorage'] !== null) {
			sessionStorage.setItem("_temp_", "_temp_");
			sessionStorage.removeItem("_temp_");
			return true;
		}
  } catch (e) {
    return false;
  }
}

if (!String.prototype.trim) {
    String.prototype.trim = function () {
        return this.replace(/^\s+|\s+$/g, '');
    };
}

function parseBoolean(string) {
    if (!string) return false;
    switch ((string + "").trim().toLowerCase()) {
		case "false": case "no": case "0": return false;
		default: return Boolean(string);
	}
}

////////////////////////////////////////////////////////
// MobileEsp device detection code

/* *******************************************
// Copyright 2010-2012, Anthony Hand
//
// File version date: April 23, 2012
//     Update:
//     - Updated DetectAmazonSilk(): Fixed an issue in the detection logic.  
//
// File version date: April 22, 2012 - Second update
//     Update: To address additional Kindle issues...
//     - Updated DetectRichCSS(): Excluded e-Ink Kindle devices. 
//     - Created DetectAmazonSilk(): Created to detect Kindle Fire devices in Silk mode. 
//     - Updated DetectMobileQuick(): Updated to include e-Ink Kindle devices and the Kindle Fire in Silk mode.  
//
// File version date: April 11, 2012
//     Update: 
//     - Added a new variable for the new BlackBerry Curve Touch (9380): deviceBBCurveTouch. 
//     - Updated DetectBlackBerryTouch() to support the new BlackBerry Curve Touch (9380). 
//
// File version date: January 21, 2012
//     Update: 
//     - Moved Windows Phone 7 to the iPhone Tier. WP7.5's IE 9-based browser is good enough now.  
//     - Added a new variable for 2 versions of the new BlackBerry Bold Touch (9900 and 9930): deviceBBBoldTouch. 
//     - Updated DetectBlackBerryTouch() to support the 2 versions of the new BlackBerry Bold Touch (9900 and 9930). 
//     - Updated DetectKindle() to focus on eInk devices only. The Kindle Fire should be detected as a regular Android device.
//
// File version date: August 22, 2011
//     Update: 
//     - Updated DetectAndroidTablet() to fix a bug introduced in the last fix! The true/false returns were mixed up. 
//
// File version date: August 16, 2011
//     Update: 
//     - Updated DetectAndroidTablet() to exclude Opera Mini, which was falsely reporting as running on a tablet device when on a phone.
//     - Updated the user agent (uagent) init technique to handle spiders and such with null values.
//
//
// LICENSE INFORMATION
// Licensed under the Apache License, Version 2.0 (the "License"); 
// you may not use this file except in compliance with the License. 
// You may obtain a copy of the License at 
//     https://www.apache.org/licenses/LICENSE-2.0 
// Unless required by applicable law or agreed to in writing, 
// software distributed under the License is distributed on an 
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
// either express or implied. See the License for the specific 
// language governing permissions and limitations under the License. 
//
//
// ABOUT THIS PROJECT
//   Project Owner: Anthony Hand
//   Email: anthony.hand@gmail.com
//   Web Site: https://www.mobileesp.com
//   Source Files: https://code.google.com/p/mobileesp/
//   
//   Versions of this code are available for:
//	  PHP, JavaScript, Java, ASP.NET (C#), and Ruby
//
//
// WARNING: 
//   These JavaScript-based device detection features may ONLY work 
//   for the newest generation of smartphones, such as the iPhone, 
//   Android and Palm WebOS devices.
//   These device detection features may NOT work for older smartphones 
//   which had poor support for JavaScript, including 
//   older BlackBerry, PalmOS, and Windows Mobile devices. 
//   Additionally, because JavaScript support is extremely poor among 
//   'feature phones', these features may not work at all on such devices.
//   For better results, consider using a server-based version of this code, 
//   such as Java, APS.NET, PHP, or Ruby.
//
// *******************************************
*/

//Initialize some initial string variables we'll look for later.
var engineWebKit = "webkit";
var deviceIphone = "iphone";
var deviceIpod = "ipod";
var deviceIpad = "ipad";
var deviceMacPpc = "macintosh"; //Used for disambiguation

var deviceAndroid = "android";
var deviceGoogleTV = "googletv";
var deviceXoom = "xoom"; //Motorola Xoom
var deviceHtcFlyer = "htc_flyer"; //HTC Flyer

var deviceNuvifone = "nuvifone"; //Garmin Nuvifone

var deviceSymbian = "symbian";
var deviceS60 = "series60";
var deviceS70 = "series70";
var deviceS80 = "series80";
var deviceS90 = "series90";

var deviceWinPhone7 = "windows phone os 7";
var deviceWinMob = "windows ce";
var deviceWindows = "windows";
var deviceIeMob = "iemobile";
var devicePpc = "ppc"; //Stands for PocketPC
var enginePie = "wm5 pie";  //An old Windows Mobile

var deviceBB = "blackberry";
var vndRIM = "vnd.rim"; //Detectable when BB devices emulate IE or Firefox
var deviceBBStorm = "blackberry95"; //Storm 1 and 2
var deviceBBBold = "blackberry97"; //Bold 97x0 (non-touch)
var deviceBBBoldTouch = "blackberry 99"; //Bold 99x0 (touchscreen)
var deviceBBTour = "blackberry96"; //Tour
var deviceBBCurve = "blackberry89"; //Curve 2
var deviceBBCurveTouch = "blackberry 938"; //Curve Touch 9380
var deviceBBTorch = "blackberry 98"; //Torch
var deviceBBPlaybook = "playbook"; //PlayBook tablet

var devicePalm = "palm";
var deviceWebOS = "webos"; //For Palm's line of WebOS devices
var deviceWebOShp = "hpwos"; //For HP's line of WebOS devices

var engineBlazer = "blazer"; //Old Palm browser
var engineXiino = "xiino";

var deviceKindle = "kindle"; //Amazon Kindle, eInk one
var engineSilk = "silk"; //Amazon's accelerated Silk browser for Kindle Fire

//Initialize variables for mobile-specific content.
var vndwap = "vnd.wap";
var wml = "wml";

//Initialize variables for random devices and mobile browsers.
//Some of these may not support JavaScript
var deviceTablet = "tablet"; //Generic term for slate and tablet devices
var deviceBrew = "brew";
var deviceDanger = "danger";
var deviceHiptop = "hiptop";
var devicePlaystation = "playstation";
var deviceNintendoDs = "nitro";
var deviceNintendo = "nintendo";
var deviceWii = "wii";
var deviceXbox = "xbox";
var deviceArchos = "archos";

var engineOpera = "opera"; //Popular browser
var engineNetfront = "netfront"; //Common embedded OS browser
var engineUpBrowser = "up.browser"; //common on some phones
var engineOpenWeb = "openweb"; //Transcoding by OpenWave server
var deviceMidp = "midp"; //a mobile Java technology
var uplink = "up.link";
var engineTelecaQ = 'teleca q'; //a modern feature phone browser

var devicePda = "pda";
var mini = "mini";  //Some mobile browsers put 'mini' in their names.
var mobile = "mobile"; //Some mobile browsers put 'mobile' in their user agent strings.
var mobi = "mobi"; //Some mobile browsers put 'mobi' in their user agent strings.

//Use Maemo, Tablet, and Linux to test for Nokia's Internet Tablets.
var maemo = "maemo";
var linux = "linux";
var qtembedded = "qt embedded"; //for Sony Mylo and others
var mylocom2 = "com2"; //for Sony Mylo also

//In some UserAgents, the only clue is the manufacturer.
var manuSonyEricsson = "sonyericsson";
var manuericsson = "ericsson";
var manuSamsung1 = "sec-sgh";
var manuSony = "sony";
var manuHtc = "htc"; //Popular Android and WinMo manufacturer

//In some UserAgents, the only clue is the operator.
var svcDocomo = "docomo";
var svcKddi = "kddi";
var svcVodafone = "vodafone";

//Disambiguation strings.
var disUpdate = "update"; //pda vs. update

//Initialize our user agent string.
var uagent = "";
if (navigator && navigator.userAgent)
    uagent = navigator.userAgent.toLowerCase();


//**************************
// Detects if the current device is an iPhone.
function DetectIphone() {
    if (uagent.search(deviceIphone) > -1) {
        //The iPad and iPod Touch say they're an iPhone! So let's disambiguate.
        if (DetectIpad() || DetectIpod())
            return false;
            //Yay! It's an iPhone!
        else
            return true;
    }
    else
        return false;
}

//**************************
// Detects if the current device is an iPod Touch.
function DetectIpod() {
    if (uagent.search(deviceIpod) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current device is an iPad tablet.
function DetectIpad() {
    if (uagent.search(deviceIpad) > -1 && DetectWebkit())
        return true;
    else
        return false;
}

//**************************
// Detects if the current device is an iPhone or iPod Touch.
function DetectIphoneOrIpod() {
    //We repeat the searches here because some iPods 
    //  may report themselves as an iPhone, which is ok.
    if (uagent.search(deviceIphone) > -1 ||
        uagent.search(deviceIpod) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects *any* iOS device: iPhone, iPod Touch, iPad.
function DetectIos() {
    if (DetectIphoneOrIpod() || DetectIpad())
        return true;
    else
        return false;
}

//**************************
// Detects *any* Android OS-based device: phone, tablet, and multi-media player.
// Also detects Google TV.
function DetectAndroid() {
    if ((uagent.search(deviceAndroid) > -1) || DetectGoogleTV())
        return true;
    //Special check for the HTC Flyer 7" tablet. It should report here.
    if (uagent.search(deviceHtcFlyer) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current device is a (small-ish) Android OS-based device
// used for calling and/or multi-media (like a Samsung Galaxy Player).
// Google says these devices will have 'Android' AND 'mobile' in user agent.
// Ignores tablets (Honeycomb and later).
function DetectAndroidPhone() {
    if (DetectAndroid() && (uagent.search(mobile) > -1))
        return true;
    //Special check for Android phones with Opera Mobile. They should report here.
    if (DetectOperaAndroidPhone())
        return true;
    //Special check for the HTC Flyer 7" tablet. It should report here.
    if (uagent.search(deviceHtcFlyer) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current device is a (self-reported) Android tablet.
// Google says these devices will have 'Android' and NOT 'mobile' in their user agent.
function DetectAndroidTablet() {
    //First, let's make sure we're on an Android device.
    if (!DetectAndroid())
        return false;

    //Special check for Opera Android Phones. They should NOT report here.
    if (DetectOperaMobile())
        return false;
    //Special check for the HTC Flyer 7" tablet. It should NOT report here.
    if (uagent.search(deviceHtcFlyer) > -1)
        return false;

    //Otherwise, if it's Android and does NOT have 'mobile' in it, Google says it's a tablet.
    if (uagent.search(mobile) > -1)
        return false;
    else
        return true;
}


//**************************
// Detects if the current device is an Android OS-based device and
//   the browser is based on WebKit.
function DetectAndroidWebKit() {
    if (DetectAndroid() && DetectWebkit())
        return true;
    else
        return false;
}


//**************************
// Detects if the current device is a GoogleTV.
function DetectGoogleTV() {
    if (uagent.search(deviceGoogleTV) > -1)
        return true;
    else
        return false;
}


//**************************
// Detects if the current browser is based on WebKit.
function DetectWebkit() {
    if (uagent.search(engineWebKit) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is the Nokia S60 Open Source Browser.
function DetectS60OssBrowser() {
    if (DetectWebkit()) {
        if ((uagent.search(deviceS60) > -1 ||
             uagent.search(deviceSymbian) > -1))
            return true;
        else
            return false;
    }
    else
        return false;
}

//**************************
// Detects if the current device is any Symbian OS-based device,
//   including older S60, Series 70, Series 80, Series 90, and UIQ, 
//   or other browsers running on these devices.
function DetectSymbianOS() {
    if (uagent.search(deviceSymbian) > -1 ||
        uagent.search(deviceS60) > -1 ||
        uagent.search(deviceS70) > -1 ||
        uagent.search(deviceS80) > -1 ||
        uagent.search(deviceS90) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is a 
// Windows Phone 7 device.
function DetectWindowsPhone7() {
    if (uagent.search(deviceWinPhone7) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is a Windows Mobile device.
// Excludes Windows Phone 7 devices. 
// Focuses on Windows Mobile 6.xx and earlier.
function DetectWindowsMobile() {
    //Exclude new Windows Phone 7.
    if (DetectWindowsPhone7())
        return false;
    //Most devices use 'Windows CE', but some report 'iemobile' 
    //  and some older ones report as 'PIE' for Pocket IE. 
    if (uagent.search(deviceWinMob) > -1 ||
        uagent.search(deviceIeMob) > -1 ||
        uagent.search(enginePie) > -1)
        return true;
    //Test for Windows Mobile PPC but not old Macintosh PowerPC.
    if ((uagent.search(devicePpc) > -1) &&
        !(uagent.search(deviceMacPpc) > -1))
        return true;
    //Test for Windwos Mobile-based HTC devices.
    if (uagent.search(manuHtc) > -1 &&
        uagent.search(deviceWindows) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is a BlackBerry of some sort.
// Includes the PlayBook.
function DetectBlackBerry() {
    if (uagent.search(deviceBB) > -1)
        return true;
    if (uagent.search(vndRIM) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is on a BlackBerry tablet device.
//  Example: PlayBook
function DetectBlackBerryTablet() {
    if (uagent.search(deviceBBPlaybook) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is a BlackBerry device AND uses a
//   WebKit-based browser. These are signatures for the new BlackBerry OS 6.
//	Examples: Torch. Includes the Playbook.
function DetectBlackBerryWebKit() {
    if (DetectBlackBerry() &&
        uagent.search(engineWebKit) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is a BlackBerry Touch
//	device, such as the Storm, Torch, and Bold Touch. Excludes the Playbook.
function DetectBlackBerryTouch() {
    if (DetectBlackBerry() &&
         ((uagent.search(deviceBBStorm) > -1) ||
         (uagent.search(deviceBBTorch) > -1) ||
         (uagent.search(deviceBBBoldTouch) > -1) ||
         (uagent.search(deviceBBCurveTouch) > -1)))
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is a BlackBerry OS 5 device AND
//	has a more capable recent browser. Excludes the Playbook.
//	Examples, Storm, Bold, Tour, Curve2
//	Excludes the new BlackBerry OS 6 and 7 browser!!
function DetectBlackBerryHigh() {
    //Disambiguate for BlackBerry OS 6 or 7 (WebKit) browser
    if (DetectBlackBerryWebKit())
        return false;
    if (DetectBlackBerry()) {
        if (DetectBlackBerryTouch() ||
           uagent.search(deviceBBBold) > -1 ||
           uagent.search(deviceBBTour) > -1 ||
           uagent.search(deviceBBCurve) > -1)
            return true;
        else
            return false;
    }
    else
        return false;
}

//**************************
// Detects if the current browser is a BlackBerry device AND
//	has an older, less capable browser. 
//	Examples: Pearl, 8800, Curve1.
function DetectBlackBerryLow() {
    if (DetectBlackBerry()) {
        //Assume that if it's not in the High tier or has WebKit, then it's Low.
        if (DetectBlackBerryHigh() || DetectBlackBerryWebKit())
            return false;
        else
            return true;
    }
    else
        return false;
}


//**************************
// Detects if the current browser is on a PalmOS device.
function DetectPalmOS() {
    //Most devices nowadays report as 'Palm', 
    //  but some older ones reported as Blazer or Xiino.
    if (uagent.search(devicePalm) > -1 ||
        uagent.search(engineBlazer) > -1 ||
        uagent.search(engineXiino) > -1) {
        //Make sure it's not WebOS first
        if (DetectPalmWebOS())
            return false;
        else
            return true;
    }
    else
        return false;
}

//**************************
// Detects if the current browser is on a Palm device
//   running the new WebOS.
function DetectPalmWebOS() {
    if (uagent.search(deviceWebOS) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is on an HP tablet running WebOS.
function DetectWebOSTablet() {
    if (uagent.search(deviceWebOShp) > -1 &&
        uagent.search(deviceTablet) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is a
//   Garmin Nuvifone.
function DetectGarminNuvifone() {
    if (uagent.search(deviceNuvifone) > -1)
        return true;
    else
        return false;
}


//**************************
// Check to see whether the device is a 'smartphone'.
//   You might wish to send smartphones to a more capable web page
//   than a dumbed down WAP page. 
function DetectSmartphone() {
    if (DetectIphoneOrIpod()
       || DetectAndroidPhone()
       || DetectS60OssBrowser()
       || DetectSymbianOS()
       || DetectWindowsMobile()
       || DetectWindowsPhone7()
       || DetectBlackBerry()
       || DetectPalmWebOS()
       || DetectPalmOS()
       || DetectGarminNuvifone())
        return true;

    //Otherwise, return false.
    return false;
};

//**************************
// Detects if the current device is an Archos media player/Internet tablet.
function DetectArchos() {
    if (uagent.search(deviceArchos) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects whether the device is a Brew-powered device.
function DetectBrewDevice() {
    if (uagent.search(deviceBrew) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects the Danger Hiptop device.
function DetectDangerHiptop() {
    if (uagent.search(deviceDanger) > -1 ||
        uagent.search(deviceHiptop) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current device is on one of 
// the Maemo-based Nokia Internet Tablets.
function DetectMaemoTablet() {
    if (uagent.search(maemo) > -1)
        return true;
    //For Nokia N810, must be Linux + Tablet, or else it could be something else.
    if ((uagent.search(linux) > -1)
        && (uagent.search(deviceTablet) > -1)
        && !DetectWebOSTablet()
        && !DetectAndroid())
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is a Sony Mylo device.
function DetectSonyMylo() {
    if (uagent.search(manuSony) > -1) {
        if (uagent.search(qtembedded) > -1 ||
            uagent.search(mylocom2) > -1)
            return true;
        else
            return false;
    }
    else
        return false;
}

//**************************
// Detects if the current browser is Opera Mobile or Mini.
function DetectOperaMobile() {
    if (uagent.search(engineOpera) > -1) {
        if (uagent.search(mini) > -1 ||
            uagent.search(mobi) > -1)
            return true;
        else
            return false;
    }
    else
        return false;
}

//**************************
// Detects if the current browser is Opera Mobile 
// running on an Android phone.
function DetectOperaAndroidPhone() {
    if ((uagent.search(engineOpera) > -1) &&
       (uagent.search(deviceAndroid) > -1) &&
       (uagent.search(mobi) > -1))
        return true;
    else
        return false;
}

//**************************
// Detects if the current browser is Opera Mobile 
// running on an Android tablet.
function DetectOperaAndroidTablet() {
    if ((uagent.search(engineOpera) > -1) &&
       (uagent.search(deviceAndroid) > -1) &&
       (uagent.search(deviceTablet) > -1))
        return true;
    else
        return false;
}

//**************************
// Detects if the current device is a Sony Playstation.
function DetectSonyPlaystation() {
    if (uagent.search(devicePlaystation) > -1)
        return true;
    else
        return false;
};

//**************************
// Detects if the current device is a Nintendo game device.
function DetectNintendo() {
    if (uagent.search(deviceNintendo) > -1 ||
     uagent.search(deviceWii) > -1 ||
     uagent.search(deviceNintendoDs) > -1)
        return true;
    else
        return false;
};

//**************************
// Detects if the current device is a Microsoft Xbox.
function DetectXbox() {
    if (uagent.search(deviceXbox) > -1)
        return true;
    else
        return false;
};

//**************************
// Detects if the current device is an Internet-capable game console.
function DetectGameConsole() {
    if (DetectSonyPlaystation())
        return true;
    if (DetectNintendo())
        return true;
    if (DetectXbox())
        return true;
    else
        return false;
};

//**************************
// Detects if the current device is an Amazon Kindle (eInk devices only).
// Note: For the Kindle Fire, use the normal Android methods.
function DetectKindle() {
    if (uagent.search(deviceKindle) > -1 &&
        !DetectAndroid())
        return true;
    else
        return false;
}

//**************************
// Detects if the current Amazon device is using the Silk Browser.
// Note: Typically used by the the Kindle Fire.
function DetectAmazonSilk() {
    if (uagent.search(engineSilk) > -1)
        return true;
    else
        return false;
}

//**************************
// Detects if the current device is a mobile device.
//  This method catches most of the popular modern devices.
//  Excludes Apple iPads and other modern tablets.
function DetectMobileQuick() {
    //Let's exclude tablets.
    if (DetectTierTablet())
        return false;

    //Most mobile browsing is done on smartphones
    if (DetectSmartphone())
        return true;

    if (uagent.search(deviceMidp) > -1 ||
     DetectBrewDevice())
        return true;

    if (DetectOperaMobile())
        return true;

    if (uagent.search(engineNetfront) > -1)
        return true;
    if (uagent.search(engineUpBrowser) > -1)
        return true;
    if (uagent.search(engineOpenWeb) > -1)
        return true;

    if (DetectDangerHiptop())
        return true;

    if (DetectMaemoTablet())
        return true;
    if (DetectArchos())
        return true;

    if ((uagent.search(devicePda) > -1) &&
         !(uagent.search(disUpdate) > -1))
        return true;
    if (uagent.search(mobile) > -1)
        return true;

    if (DetectKindle() ||
        DetectAmazonSilk())
        return true;

    return false;
};


//**************************
// Detects in a more comprehensive way if the current device is a mobile device.
function DetectMobileLong() {
    if (DetectMobileQuick())
        return true;
    if (DetectGameConsole())
        return true;
    if (DetectSonyMylo())
        return true;

    //Detect for certain very old devices with stupid useragent strings.
    if (uagent.search(manuSamsung1) > -1 ||
     uagent.search(manuSonyEricsson) > -1 ||
     uagent.search(manuericsson) > -1)
        return true;

    if (uagent.search(svcDocomo) > -1)
        return true;
    if (uagent.search(svcKddi) > -1)
        return true;
    if (uagent.search(svcVodafone) > -1)
        return true;


    return false;
};


//*****************************
// For Mobile Web Site Design
//*****************************

//**************************
// The quick way to detect for a tier of devices.
//   This method detects for the new generation of
//   HTML 5 capable, larger screen tablets.
//   Includes iPad, Android (e.g., Xoom), BB Playbook, WebOS, etc.
function DetectTierTablet() {
    if (DetectIpad()
         || DetectAndroidTablet()
         || DetectBlackBerryTablet()
         || DetectWebOSTablet())
        return true;
    else
        return false;
};

//**************************
// The quick way to detect for a tier of devices.
//   This method detects for devices which can 
//   display iPhone-optimized web content.
//   Includes iPhone, iPod Touch, Android, Windows Phone 7, WebOS, etc.
function DetectTierIphone() {
    if (DetectIphoneOrIpod())
        return true;
    if (DetectAndroidPhone())
        return true;
    if (DetectBlackBerryWebKit() && DetectBlackBerryTouch())
        return true;
    if (DetectWindowsPhone7())
        return true;
    if (DetectPalmWebOS())
        return true;
    if (DetectGarminNuvifone())
        return true;
    else
        return false;
};

//**************************
// The quick way to detect for a tier of devices.
//   This method detects for devices which are likely to be 
//   capable of viewing CSS content optimized for the iPhone, 
//   but may not necessarily support JavaScript.
//   Excludes all iPhone Tier devices.
function DetectTierRichCss() {
    if (DetectMobileQuick()) {
        //Exclude iPhone Tier and e-Ink Kindle devices
        if (DetectTierIphone() || DetectKindle())
            return false;

        //The following devices are explicitly ok.
        if (DetectWebkit())
            return true;
        if (DetectS60OssBrowser())
            return true;

        //Note: 'High' BlackBerry devices ONLY
        if (DetectBlackBerryHigh())
            return true;

        //Older Windows 'Mobile' isn't good enough for iPhone Tier.
        if (DetectWindowsMobile())
            return true;

        if (uagent.search(engineTelecaQ) > -1)
            return true;

        else
            return false;
    }
    else
        return false;
};

//**************************
// The quick way to detect for a tier of devices.
//   This method detects for all other types of phones,
//   but excludes the iPhone and RichCSS Tier devices.
// NOTE: This method probably won't work due to poor
//  support for JavaScript among other devices. 
function DetectTierOtherPhones() {
    if (DetectMobileLong()) {
        //Exclude devices in the other 2 categories
        if (DetectTierIphone() || DetectTierRichCss())
            return false;

            //Otherwise, it's a YES
        else
            return true;
    }
    else
        return false;
};

// generated from detectmobilebrowsers.com.   This is to detect non mobile browser - i.e. Desktop category.
function DetectDesktop() {
    var a = uagent.toLowerCase();
    var isMobile = (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4)));

    if (isMobile)
        return false;
    else
        return true;
}






//Flyout Script
function MoxieFlyoutReset() { return {
	TOP: 0,
	RIGHT: 1,
	BOTTOM: 2,
	LEFT: 3,
	
	OPENUPPOINT: 60,
	
	SHORT_DELAY: 100,
	LONG_DELAY: 1000,

	side: this.RIGHT,
	sideOffset: 25,//percent
	color: "#0000a0",//'tab' color
	text: "Chat Now",
	textColor: "#f0f0f0",
	openWidth: "480px",
	openHeight: "480px",
	backColor: "rgba(0,0,0,0.9)",
	titleColor: "rgb(0,162,232)",
	titleTextColor: "#f0f0f0",
	btnColor: "rgb(0,162,232)",     //top bar 2 buttons background color
	tabFont: "12pt Tahoma",
	titleFont: "12pt Tahoma",
	fullscreen: false,
	tabClass: "",
	startOpen: "",
	serverUrl: "/",
	portalUrl: "about:blank",
	openUrl: null,
	portalId: null,
	portalStyle: null,
	portalQuestionnaire: null,
	newChatPortalId: null,
	newChatPortalStyle: null,
	newCHatQuestionnaire: null,
	pageRoleElemOrigStyle: null,
	isSafari: false,
	isTabInfoRequestOccured: false,
	queryStringType: 
		{
			FullScreen: 1
		},

	css: '\
	.fixed{ position: fixed; height: 100%; } \n\
	#MoxieFlyoutHolder{ \n\
        animation: none;\n\
        animation-delay: 0;\n\
        animation-direction: normal;\n\
        animation-duration: 0;\n\
        animation-fill-mode: none;\n\
        animation-iteration-count: 1;\n\
        animation-name: none;\n\
        animation-play-state: running;\n\
        animation-timing-function: ease;\n\
        backface-visibility: visible;\n\
        background: 0;\n\
        background-attachment: scroll;\n\
        background-clip: border-box;\n\
        background-color: transparent;\n\
        background-image: none;\n\
        background-origin: padding-box;\n\
        background-position: 0 0;\n\
        background-position-x: 0;\n\
        background-position-y: 0;\n\
        background-repeat: repeat;\n\
        background-size: auto auto;\n\
        border: 0;\n\
        border-style: none;\n\
        border-width: medium;\n\
        border-color: inherit;\n\
        border-bottom: 0;\n\
        border-bottom-color: inherit;\n\
        border-bottom-left-radius: 0;\n\
        border-bottom-right-radius: 0;\n\
        border-bottom-style: none;\n\
        border-bottom-width: medium;\n\
        border-collapse: separate;\n\
        border-image: none;\n\
        border-left: 0;\n\
        border-left-color: inherit;\n\
        border-left-style: none;\n\
        border-left-width: medium;\n\
        border-radius: 0;\n\
        border-right: 0;\n\
        border-right-color: inherit;\n\
        border-right-style: none;\n\
        border-right-width: medium;\n\
        border-spacing: 0;\n\
        border-top: 0;\n\
        border-top-color: inherit;\n\
        border-top-left-radius: 0;\n\
        border-top-right-radius: 0;\n\
        border-top-style: none;\n\
        border-top-width: medium;\n\
        bottom: auto;\n\
        box-shadow: none;\n\
        box-sizing: content-box;\n\
        caption-side: top;\n\
        clear: none;\n\
        clip: auto;\n\
        columns: auto;\n\
        column-count: auto;\n\
        column-fill: balance;\n\
        column-gap: normal;\n\
        column-rule: medium none currentColor;\n\
        column-rule-color: currentColor;\n\
        column-rule-style: none;\n\
        column-rule-width: none;\n\
        column-span: 1;\n\
        column-width: auto;\n\
        content: normal;\n\
        counter-increment: none;\n\
        counter-reset: none;\n\
        cursor: auto;\n\
        direction: ltr;\n\
        display: block;\n\
        empty-cells: show;\n\
        float: none;\n\
        font: normal;\n\
        font-family: inherit;\n\
        font-size: medium;\n\
        font-style: normal;\n\
        font-variant: normal;\n\
        font-weight: normal;\n\
        height: auto;\n\
        hyphens: none;\n\
        left: auto;\n\
        letter-spacing: normal;\n\
        line-height: normal;\n\
        list-style: none;\n\
        list-style-image: none;\n\
        list-style-position: outside;\n\
        list-style-type: disc;\n\
        margin: 0;\n\
        margin-bottom: 0;\n\
        margin-left: 0;\n\
        margin-right: 0;\n\
        margin-top: 0;\n\
        max-height: none;\n\
        max-width: none;\n\
        min-height: 0;\n\
        min-width: 0;\n\
        opacity: 1;\n\
        orphans: 0;\n\
        outline: 0;\n\
        outline-color: invert;\n\
        outline-style: none;\n\
        outline-width: medium;\n\
        overflow: visible;\n\
        overflow-x: visible;\n\
        overflow-y: visible;\n\
        padding: 0;\n\
        padding-bottom: 0;\n\
        padding-left: 0;\n\
        padding-right: 0;\n\
        padding-top: 0;\n\
        page-break-after: auto;\n\
        page-break-before: auto;\n\
        page-break-inside: auto;\n\
        perspective: none;\n\
        perspective-origin: 50% 50%;\n\
        position: static;\n\
        right: auto;\n\
        tab-size: 8;\n\
        table-layout: auto;\n\
        text-align: inherit;\n\
        text-align-last: auto;\n\
        text-decoration: none;\n\
        text-decoration-color: inherit;\n\
        text-decoration-line: none;\n\
        text-decoration-style: solid;\n\
        text-indent: 0;\n\
        text-shadow: none;\n\
        text-transform: none;\n\
        top: auto;\n\
        transform-style: flat;\n\
        transition: none;\n\
        transition-delay: 0s;\n\
        transition-duration: 0s;\n\
        transition-property: none;\n\
        transition-timing-function: ease;\n\
        unicode-bidi: normal;\n\
        vertical-align: baseline;\n\
        visibility: visible;\n\
        white-space: normal;\n\
        widows: 0;\n\
        width: auto;\n\
        word-spacing: normal;\n\
		color: %textColor%;\n\
		z-index: 10000;\n\
	}\n\
	#ErrorCover { \n\
		display: none; \n\
		position: fixed; \n\
		top: 0; \n\
		right: 0; \n\
		bottom: 0; \n\
		left: 0; \n\
		opacity: 1; \n\
		z-index: 10001; \n\
		background-color: %titleColor%; \n\
		color: %titleTextColor%; \n\
		font:  %titleFont%; \n\
		padding: 20% 0 20% 0; \n\
		text-align: center; \n\
	}\n\
	#MoxieFlyoutHolder{\n\
		border: none !important;\n\
	}\n\
    #MoxieFlyoutHolder,#MoxieFlyoutTab,#MoxieFlyoutPanel{\n\
        z-index: 10000;\n\
    }\n\
	#MoxieFlyoutTab{\n\
		position: fixed;\n\
		padding: 5px;\n\
		background: %color%;\n\
		cursor: pointer;\n\
		font: %tabFont%;\n\
		height: 2em;\n\
		min-height: 25px;\n\
		line-height: 2em;\n\
		transition: opacity 0.5s;\n\
		white-space: nowrap;\n\
	}\n\
	.MoxieFlyoutOpen #MoxieFlyoutTab {\n\
		opacity: 0;\n\
	}\n\
	#MoxieFlyoutTab > img{\n\
		margin-left: .8em;\n\
		margin-right: .3em;\n\
		height: 1em;\n\
		vertical-align: text-bottom;\n\
	}\n\
	#MoxieFlyoutTabText{\n\
		margin-right: 0.8em;\n\
	}\n\
	    #MoxieFlyoutTabText a {\n\
        color: inherit;\n\
        text-decoration: none;\n\
    }\n\
	.MoxieFlyoutRight #MoxieFlyoutTab{\n\
		right: 0px;\n\
		top: %offset%%;\n\
	}\n\
	.MoxieFlyoutLeft #MoxieFlyoutTab{\n\
		left: 0px;\n\
		top: %offset%%;\n\
	}\n\
	.MoxieFlyoutBottom #MoxieFlyoutTab{\n\
		bottom: 0px;\n\
		left: %offset%%;\n\
	}\n\
	.MoxieFlyoutTop #MoxieFlyoutTab{\n\
		top: 0px;\n\
		left: %offset%%;\n\
	}\n\
    .MoxieFlyoutBottom.MoxieFlyoutFarSide #MoxieFlyoutTab, .MoxieFlyoutTop.MoxieFlyoutFarSide #MoxieFlyoutTab {\n\
        -webkit-transform: translate(-100%, 0px);\n\
        -moz-transform:  translate(-100%, 0px);\n\
        -o-transform: translate(-100%, 0px);\n\
        -ms-transform:  translate(-100%, 0px);\n\
        transform:  translate(-100%, 0px);\n\
    }\n\
	.MoxieFlyoutRight #MoxieFlyoutTab ,.MoxieFlyoutLeft #MoxieFlyoutTab, .MoxieFlyoutBottom #MoxieFlyoutTab{\n\
		border-top-right-radius: 5px;\n\
		border-top-left-radius: 5px;\n\
	}\n\
	.MoxieFlyoutTop #MoxieFlyoutTab{\n\
		border-bottom-right-radius: 5px;\n\
		border-bottom-left-radius: 5px;\n\
	}\n\
	.MoxieFlyoutRight #MoxieFlyoutTab{\n\
		-webkit-transform-origin: 100% 0%;\n\
        -webkit-transform: rotate(-90deg) translate(0px,-100%);\n\
        -moz-transform-origin: 100% 0%;\n\
        -moz-transform: rotate(-90deg) translate(0px,-100%);\n\
        -o-transform-origin: 100% 0%;\n\
        -o-transform: rotate(-90deg) translate(0px,-100%);\n\
        -ms-transform-origin: 100% 0%;\n\
        -ms-transform: rotate(-90deg) translate(0px,-100%);\n\
        transform-origin: 100% 0%;\n\
        transform: rotate(-90deg) translate(0px,-100%);\n\
	}\n\
	.MoxieFlyoutLeft #MoxieFlyoutTab{\n\
		-webkit-transform-origin: 0% 0%;\n\
        -webkit-transform: rotate(90deg) translate(0px,-100%);\n\
        -moz-transform-origin: 0% 0%;\n\
        -moz-transform: rotate(90deg) translate(0px,-100%);\n\
        -o-transform-origin: 0% 0%;\n\
        -o-transform: rotate(90deg) translate(0px,-100%);\n\
        -ms-transform-origin: 0% 0%;\n\
        -ms-transform: rotate(90deg) translate(0px,-100%);\n\
        transform-origin: 0% 0%;\n\
        transform: rotate(90deg) translate(0px,-100%);\n\
	}\n\
	.MoxieFlyoutRight.MoxieFlyoutFarSide #MoxieFlyoutTab {\n\
		-webkit-transform-origin: 100% 0px;\n\
        -webkit-transform: rotate(-90deg) translate( 100%,-100%);\n\
        -moz-transform-origin: 100% 0px;\n\
        -moz-transform: rotate(-90deg) translate( 100%,-100%);\n\
        -o-transform-origin: 100% 0px;\n\
        -o-transform: rotate(-90deg) translate( 100%,-100%);\n\
        -ms-transform-origin: 100% 0px;\n\
        -ms-transform: rotate(-90deg) translate( 100%,-100%);\n\
        transform-origin: 100% 0px;\n\
        transform: rotate(-90deg) translate( 100%,-100%);\n\
	}\n\
	.MoxieFlyoutLeft.MoxieFlyoutFarSide #MoxieFlyoutTab {\n\
		-webkit-transform-origin: 0% 0%;\n\
        -webkit-transform: rotate(90deg) translate(-100%,-100%);\n\
        -moz-transform-origin: 0% 0%;\n\
        -moz-transform: rotate(90deg) translate(-100%,-100%);\n\
        -o-transform-origin: 0% 0%;\n\
        -o-transform: rotate(90deg) translate(-100%,-100%);\n\
        -ms-transform-origin: 0% 0%;\n\
        -ms-transform: rotate(90deg) translate(-100%,-100%);\n\
        transform-origin: 0% 0%;\n\
        transform: rotate(90deg) translate(-100%,-100%);\n\
	}\n\
	.MoxieFlyoutFullscreen #MoxieFlyoutPanel{\n\
		position: fixed !important;\n\
		top: 0px !important;\n\
		bottom: 0px !important;\n\
		left: 0px !important;\n\
		right: 0px !important;\n\
		border-radius: 0 !important;\n\
	}\n\
	.MoxieFlyoutRight.MoxieFlyoutToFull #MoxieFlyoutPanel{\n\
		position: fixed !important;\n\
        top: 0px !important;\n\
		bottom: 0px !important;\n\
	}\n\
	.MoxieFlyoutLeft.MoxieFlyoutToFull #MoxieFlyoutPanel{\n\
		position: fixed !important;\n\
        top: 0px !important;\n\
		bottom: 0px !important;\n\
	}\n\
	.MoxieFlyoutBottom.MoxieFlyoutToFull #MoxieFlyoutPanel{\n\
		position: fixed !important;\n\
        left: 0px !important;\n\
		right: 0px !important;\n\
	}\n\
	.MoxieFlyoutTop.MoxieFlyoutToFull #MoxieFlyoutPanel{\n\
		position: fixed !important;\n\
        left: 0px !important;\n\
		right: 0px !important;\n\
	}\n\
	#MoxieFlyoutPanel{\n\
		position: fixed;\n\
		background: %backColor%;\n\
		visibility: hidden;\n\
		width: %width%;\n\
		height: %height%;\n\
		border: 1px solid %titleColor%;\n\
	}\n\
	.MoxieFlyoutRight #MoxieFlyoutPanel{\n\
		border-radius: 5px 1px 1px 5px;\n\
        top: %offset%%;\n\
        right: -%width%;\n\
        transition:opacity 1s,left 1s, right 1s;\n\
	}\n\
	.MoxieFlyoutLeft #MoxieFlyoutPanel{\n\
		border-radius: 1px 5px 5px 1px;\n\
        top: %offset%%;\n\
        left: -%width%;\n\
        transition:opacity 1s,left 1s, right 1s;\n\
	}\n\
	.MoxieFlyoutTop #MoxieFlyoutPanel{\n\
		border-radius: 1px 1px 5px 5px;\n\
        left: %offset%%;\n\
        top: -%height%;\n\
        transition: opacity 1s, top 1s, bottom 1s;\n\
	}\n\
	.MoxieFlyoutBottom #MoxieFlyoutPanel{\n\
		border-radius: 5px 5px 1px 1px;\n\
        left: %offset%%;\n\
        bottom: -%height%;\n\
        transition: opacity 1s, top 1s, bottom 1s;\n\
	}\n\
	.MoxieFlyoutTop.MoxieFlyoutFarSide #MoxieFlyoutPanel, .MoxieFlyoutBottom.MoxieFlyoutFarSide #MoxieFlyoutPanel{\n\
		-webkit-transform: translate(-100%, 0px);\n\
        -moz-transform: translate(-100%, 0px);\n\
        -o-transform: translate(-100%, 0px);\n\
        -ms-transform: translate(-100%, 0px);\n\
        transform: translate(-100%, 0px);\n\
	}\n\
	.MoxieFlyoutRight.MoxieFlyoutFarSide #MoxieFlyoutPanel, .MoxieFlyoutLeft.MoxieFlyoutFarSide #MoxieFlyoutPanel{\n\
		-webkit-transform: translate(0px, -100%);\n\
        -moz-transform: translate(0px, -100%);\n\
        -o-transform: translate(0px, -100%);\n\
        -ms-transform: translate(0px, -100%);\n\
        transform: translate(0px, -100%);\n\
	}\n\
    .MoxieFlyoutTop.MoxieFlyoutFarSide.MoxieFlyoutFullscreen #MoxieFlyoutPanel, .MoxieFlyoutBottom.MoxieFlyoutFarSide.MoxieFlyoutFullscreen #MoxieFlyoutPanel,\n\
    .MoxieFlyoutTop.MoxieFlyoutFarSide.MoxieFlyoutToFull #MoxieFlyoutPanel, .MoxieFlyoutBottom.MoxieFlyoutFarSide.MoxieFlyoutToFull #MoxieFlyoutPanel,\n\
	.MoxieFlyoutRight.MoxieFlyoutFarSide.MoxieFlyoutFullscreen #MoxieFlyoutPanel, .MoxieFlyoutLeft.MoxieFlyoutFarSide.MoxieFlyoutFullscreen #MoxieFlyoutPanel,\n\
    .MoxieFlyoutRight.MoxieFlyoutFarSide.MoxieFlyoutToFull #MoxieFlyoutPanel, .MoxieFlyoutLeft.MoxieFlyoutFarSide.MoxieFlyoutToFull #MoxieFlyoutPanel{\n\
		-webkit-transform:  translate(0px, 0px) !important;\n\
        -moz-transform:  translate(0px, 0px) !important;\n\
        -o-transform:  translate(0px, 0px) !important;\n\
        -ms-transform:  translate(0px, 0px) !important;\n\
        transform:  translate(0px, 0px) !important;\n\
	}\n\
	.MoxieFlyoutRight #MoxieFlyoutPanel #MoxieFlyoutTitle{\n\
		border-radius: 3px 1px 1px 1px;\n\
	}\n\
	.MoxieFlyoutLeft #MoxieFlyoutPanel #MoxieFlyoutTitle{\n\
		border-radius: 1px 3px 1px 1px;\n\
	}\n\
	.MoxieFlyoutBottom #MoxieFlyoutPanel #MoxieFlyoutTitle{\n\
		border-radius: 3px 3px 1px 1px;\n\
	}\n\
	.MoxieFlyoutFullscreen #MoxieFlyoutPanel #MoxieFlyoutTitle{\n\
		border-radius: 0 !important;\n\
	}\n\
	.MoxieFlyoutOpen #MoxieFlyoutPanel{\n\
		visibility: visible;\n\
	}\n\
    .MoxieFlyoutClosing #MoxieFlyoutPanel{\n\
		visibility: visible !important;\n\
	}\n\
    .MoxieFlyoutClosing #MoxieFlyoutTab{\n\
		opacity: 0 !important;\n\
	}\n\
    .MoxieFlyoutOpen.MoxieFlyoutRight #MoxieFlyoutPanel{\n\
        right: 0;\n\
	}\n\
	.MoxieFlyoutOpen.MoxieFlyoutLeft #MoxieFlyoutPanel{\n\
        left: 0;\n\
	}\n\
	.MoxieFlyoutOpen.MoxieFlyoutTop #MoxieFlyoutPanel{\n\
        top: 0;\n\
	}\n\
	.MoxieFlyoutOpen.MoxieFlyoutBottom #MoxieFlyoutPanel{\n\
        bottom: 0;\n\
	}\n\
	#MoxieFlyoutTitle{\n\
		height: 40px;\n\
		background: %titleColor%;\n\
		color: %titleTextColor%;\n\
		font: %titleFont%;\n\
		text-align: center;\n\
		line-height: 1.5em;\n\
		overflow: hidden;\n\
	}\n\
    #MoxieFlyoutTitle button {\n\
        min-height: 40px;\n\
        margin: 0 10px;\n\
        padding: 0;\n\
        border: none;\n\
		background: %btnColor%;\n\
		color: inherit;\n\
		font: inherit;\n\
		cursor: pointer;\n\
    }\n\
	#MoxieFlyoutBtn1{\n\
		float: left;\n\
		display: none;\n\
	}\n\
	#MoxieFlyoutBtn2{\n\
		float: right;\n\
		display: none;\n\
	}\n\
	#MoxieFlyoutFrameHolder{\n\
		position: absolute;\n\
		top: 40px;\n\
		bottom: 2px;\n\
		left: 2px;\n\
		right: 2px;\n\
	}\n\
    .MoxieFlyoutFullscreen #MoxieFlyoutFrameHolder {\n\
        top: 40px;\n\
        left: 0;\n\
        bottom: 0;\n\
        right: 0;\n\
    }\n\
	#MoxieFlyoutPanel iframe{\n\
		width:100%;\n\
		height:100%;\n\
		border: none;\n\
	}\n\
	.MoxieFlyoutTop #MoxieFlyoutTabAlert{\n\
		bottom: 0.3em;\n\
	}\n\
	.MoxieFlyoutBottom #MoxieFlyoutTabAlert, .MoxieFlyoutLeft #MoxieFlyoutTabAlert, .MoxieFlyoutRight #MoxieFlyoutTabAlert{\n\
		top: 0.3em;\n\
	}\n\
	#MoxieFlyoutTabAlert{\n\
		display:none;\n\
		position: absolute;\n\
		width: 0.5em;\n\
		height: 0.5em;\n\
		border-radius: 50%;\n\
		box-shadow: 0 0 2em 0.5em;\n\
		-webkit-box-shadow: 0 0 2em 0.5em;\n\
		\n\
		animation-name: MoxieFlyoutPulse;\n\
		animation-duration: 1s;\n\
		animation-iteration-count: infinite;\n\
		animation-direction: alternate;\n\
		animation-play-state: running;\n\
		-webkit-animation-name: MoxieFlyoutPulse;\n\
		-webkit-animation-duration: 1s;\n\
		-webkit-animation-iteration-count: infinite;\n\
		-webkit-animation-direction: alternate;\n\
		-webkit-animation-play-state: running;\n\
	}\n\
	\n\
	@keyframes MoxieFlyoutPulse{\n\
		0%   {opacity: 1.0;}\n\
		100% {opacity: 0.5;}\n\
	}\n\
	@-webkit-keyframes MoxieFlyoutPulse{\n\
		0%   {opacity: 1.0;}\n\
		100% {opacity: 0.5;}\n\
	}\n\
    .screenReader {\n\
        position: absolute;\n\
        left: -1000px;\n\
        top: auto;\n\
        width: 1px;\n\
        height: 1px;\n\
        overflow: hidden;\n\
    }\n\
	',

	htmltab: '\
	<div id=MoxieFlyoutTab onclick="MoxieFlyout.open();">\n\
		<img src="%serverUrl%icon_chat.png" alt="%text%" id=MoxieFlyoutTabIcon>\n\
		<span id=MoxieFlyoutTabText><a href="#">%text%</a></span>\n\
		<div id=MoxieFlyoutTabAlert></div>\n\
	</div>',
	htmlpanel: '<div id=MoxieFlyoutPanel>\n\
        <span aria-label="Start of chat region" tabindex="0" class="screenReader">Start of chat region</span>\n\
		<div id=ErrorCover></div>\n\
		<div id=MoxieFlyoutTitle>\n\
			<button id=MoxieFlyoutBtn1 onclick="MoxieFlyout.btnClick(this);MoxieFlyout.close();">%btn1text%</button>\n\
			<button id=MoxieFlyoutBtn2 onclick="MoxieFlyout.btnClick(this);disposeOfMoxieFlyoutWindow();">%btn2text%</button>\n\
			<span id=MoxieFlyoutTitleText></span>\n\
		</div>\n\
		<div id=MoxieFlyoutFrameHolder>\n\
			<iframe id=MoxieFlyoutIframe src="about:blank" title="%text%"></iframe>\n\
		</div>\n\
        <span aria-label="End of chat region" tabindex="0" class="screenReader">End of chat region</span>\n\
	</div>\n\
	',

	html_noSessionStorage: '\
		<html>\n\
			<head>\n\
				<meta charset="utf-8">\n\
				<meta http-equiv="X-UA-Compatible" content="IE=edge">\n\
				<meta name="viewport" content="width=device-width, initial-scale=1">\n\
				<title>Error - Disable Private Mode</title>\n\
			</head>\n\
			<body>\n\
				<div class="no-SessionStorage" style="margin: auto;"><p>We have detected your browser is in Private Mode or cookies are disabled.</p><p>Please disable Private Mode and enable cookies to engage in chat.</p></div>\n\
			</body>\n\
		</html>\n\
	',

    init: function (params) {
		//step 1, save parameters
		MoxieFlyout.portalId = params.portalID;
		MoxieFlyout.portalStyle = params.style;
		MoxieFlyout.portalQuestionnaire = params.questionnaire;
		MoxieFlyout.side = params.flySide;
		MoxieFlyout.offset = params.sideOffset;
		MoxieFlyout.color = params.tabColor;
		MoxieFlyout.text = hTMLEncode(params.tabText);
		MoxieFlyout.textColor = params.tabTextColor;
		MoxieFlyout.openWidth = params.flyWidth;
		MoxieFlyout.openHeight = params.flyHeight;
		MoxieFlyout.fullscreen = params.isFullscreen;
		MoxieFlyout.backColor = params.flyBackColor;
		MoxieFlyout.titleColor = params.flyTitleColor;
		MoxieFlyout.titleTextColor = params.flyTitleTextColor;
		MoxieFlyout.btnColor = params.flyBtnColor;
		MoxieFlyout.tabFont = params.fontTab;
		MoxieFlyout.titleFont = params.fontTitle;
		MoxieFlyout.serverUrl = params.serverURL;
		MoxieFlyout.portalUrl = params.portalURL;
		MoxieFlyout.newChatPortalId = params.currentPagePortalId;
		MoxieFlyout.newChatPortalStyle = params.currentPagePortalStyle;
		MoxieFlyout.newCHatQuestionnaire = params.currentPageQuestionnaire;
		MoxieFlyout.openUrl = params.openUrl;
		MoxieFlyout.deviceType = params.deviceType;
		var startopen = params.startOpen;
		setTimeout(function () { MoxieFlyout.getWindowDimensions(); }, MoxieFlyout.LONG_DELAY * 2); //retrieves initial dimensions
		
		//step 2, verify settings
        if (MoxieFlyout.side < MoxieFlyout.TOP || MoxieFlyout.side > MoxieFlyout.LEFT) {
			MoxieFlyout.side = MoxieFlyout.RIGHT;
		}
		//TODO verify other settings if possible
		
		//step 3, setup html / css
		MoxieFlyout.setSettings(startopen);

        var cssp = MoxieFlyout.parse(MoxieFlyout.css);
		var htmltp = MoxieFlyout.parse(MoxieFlyout.htmltab);
		var htmlpp = MoxieFlyout.parse(MoxieFlyout.htmlpanel);

		//step 4, inject into page
        //style
		var style = document.getElementById("MoxieFlyoutStyle");
		if (style) {
		    style.innerHTML = cssp;
		} else {
		var head = document.getElementsByTagName('head')[0];
			if (head) {
		        style = document.createElement('style');
			head.appendChild(style);
                style.id = "MoxieFlyoutStyle";
		        style.type = "text/css";
		        if (style.styleSheet) { //For IE Compatibility mode
		            style.styleSheet.cssText = cssp;
			} else {
		            style.appendChild(document.createTextNode(cssp)); //everything else
			}
		    } else if (console != null) {
		        console.log("Unable to setup MoxieFlyout due to missing HEAD");
		    }
		}
	    //html
		var div = document.getElementById("MoxieFlyoutHolder");
		if (div) {
		    div.className = MoxieFlyout.tabClass;
		        div.innerHTML = htmltp + htmlpp;
		    } else {
			var body = document.getElementsByTagName('body')[0];
		    if (body != null) {
				var div = document.createElement('div');
				div.id = "MoxieFlyoutHolder";
		        div.className = MoxieFlyout.tabClass;
		        div.innerHTML = htmltp + htmlpp;
                div.setAttribute("role", "region");
                div.setAttribute("aria-labelledby", "MoxieFlyoutTabText");
				body.appendChild(div);
		    } else if (console != null) {
				console.log("Unable to setup MoxieFlyout due to missing BODY");
		    }
		}
		
        //step 5 add listeners and final touches
		if (startopen) {
            if (MoxieFlyout.openUrl)
				MoxieFlyout.setFlyoutContent(MoxieFlyout.openUrl);

			if (supports_html5_storage()) {
                MoxieFlyout.storage.setItem("MoxieFlyout.isOpen", true);
                MoxieFlyout.storage.setItem("MoxieFlyout.portal", MoxieFlyout.portalId);
                MoxieFlyout.storage.setItem("MoxieFlyout.style", MoxieFlyout.portalStyle);
                MoxieFlyout.storage.setItem("MoxieFlyout.quest", MoxieFlyout.portalQuestionnaire);
			}

			MoxieFlyout.hostPage.alter();
			}
		if (!window.addEventListener) {
			window.attachEvent("message", MoxieFlyout.processMessage);
			window.attachEvent("onresize", MoxieFlyout.onResize);
			window.attachEvent("onfocus", MoxieFlyout.setIframeFocus);
		} else {
			window.addEventListener("message", MoxieFlyout.processMessage, false);
			window.addEventListener('orientationchange', function(e) { setTimeout(function() { MoxieFlyout.onResize(e) }, 250)});
			window.addEventListener("focus", MoxieFlyout.setIframeFocus);
		}
		if (supports_html5_storage()) {
            var color = MoxieFlyout.storage.getItem("MoxieFlyout.alert");
			if (color != null && color.length > 3) {
				MoxieFlyout.setAlert(color);
			}
		}

		MoxieFlyout.isSafari = MoxieFlyout.isSafariBrowser();
	},
	setSettings: function (startopen) {

		var height;
		var width;
		if (document.documentElement && document.documentElement.clientWidth) {
			//this excludes the space scrollbars take up
			width = document.documentElement.clientWidth;
			height = document.documentElement.clientHeight;
		} else {
			//this will include scrollbar size, so we actually have a bit less room than this
			width = window.innerWidth;
			height = window.innerHeight
		}

		switch (parseInt(MoxieFlyout.side)) {
			case MoxieFlyout.TOP: {
				MoxieFlyout.tabClass = "MoxieFlyoutTop";
                if (!MoxieFlyout.fullscreen)
				MoxieFlyout.offset = MoxieFlyout.calcOffest(MoxieFlyout.offset, MoxieFlyout.openWidth, width);
			}
				break;
			case MoxieFlyout.BOTTOM: {
				MoxieFlyout.tabClass = "MoxieFlyoutBottom";
			    if (!MoxieFlyout.fullscreen)
				MoxieFlyout.offset = MoxieFlyout.calcOffest(MoxieFlyout.offset, MoxieFlyout.openWidth, width);
			}
				break;
			case MoxieFlyout.LEFT: {
				MoxieFlyout.tabClass = "MoxieFlyoutLeft";
				if (!MoxieFlyout.fullscreen) {
				MoxieFlyout.offset = MoxieFlyout.calcOffest(MoxieFlyout.offset, MoxieFlyout.openHeight, height);
			}
			    if (MoxieFlyout.deviceType == 2 && MoxieFlyout.iOSVersion().major != null) { //IPad
			    	MoxieFlyout.offset = 8.5;
			    }
			}
				break;
			case MoxieFlyout.RIGHT:
			default: {
				MoxieFlyout.tabClass = "MoxieFlyoutRight";
				if (!MoxieFlyout.fullscreen) {
				MoxieFlyout.offset = MoxieFlyout.calcOffest(MoxieFlyout.offset, MoxieFlyout.openHeight, height);
			}
				if (MoxieFlyout.deviceType == 2 && MoxieFlyout.iOSVersion().major != null) { //IPad
					MoxieFlyout.offset = 8.5;
		}
			}
		}
		if (startopen == true) {
		    MoxieFlyout.tabClass += " MoxieFlyoutOpen";
		}
		if (MoxieFlyout.offset > MoxieFlyout.OPENUPPOINT) {
			MoxieFlyout.tabClass += " MoxieFlyoutFarSide";
		} else {
			MoxieFlyout.tabClass += " MoxieFlyoutNearSide";
		}
		if (MoxieFlyout.fullscreen) {
			MoxieFlyout.openWidth = "100%";
			MoxieFlyout.openHeight = "100%";
            if (startopen)
			    MoxieFlyout.tabClass += " MoxieFlyoutFullscreen";
		}
	},

	calcOffest: function (percent, length, totalsize) {
		var offset = MoxieFlyout.offset;
		var len = 0;
		if (length.indexOf("px") > 0) {
			len = parseInt(length)
		} else if (length.indexOf("%") > 0) {
			len = totalsize * (parseInt(length) / 100);
		} else {
			return offset;
			//todo handle em and other relative distances (currently can't be set in the admin)
		}

		if (MoxieFlyout.offset > MoxieFlyout.OPENUPPOINT) {
			//opening above offest point
			var pointPixels = totalsize * (offset / 100);
			while ((pointPixels < len) && (offset < 100)) {
				offset++;
				pointPixels = totalsize * (offset / 100);
			}
		} else {
			//opening below offset point
			var pointPixels = totalsize * (offset / 100);
			while (((totalsize - pointPixels) < len) && (offset > 0)) {
				offset--;
				pointPixels = totalsize * (offset / 100);
			}
		}
		return offset;
	},

    open: function () {
	    var fly = document.getElementById('MoxieFlyoutHolder');
	    if (fly != null) {
	        if (MoxieFlyout.hasClass(fly, 'MoxieFlyoutOpen'))
				return;

			MoxieFlyout.hostPage.alter();

			if (MoxieFlyout.fullscreen) {
			    MoxieFlyout.addClass(fly, 'MoxieFlyoutToFull');
			}
			MoxieFlyout.addClass(fly, 'MoxieFlyoutOpen');
			setTimeout(MoxieFlyout.open2, MoxieFlyout.LONG_DELAY);
			
        } else if (console != null) {
			console.log("Unable to show MoxieFlyoutPanel");
		}
		MoxieFlyout.setAlert(null);
		if (MoxieFlyout.openUrl) {
			MoxieFlyout.setFlyoutContent(MoxieFlyout.openUrl);
			MoxieFlyout.openUrl = null;
		}
		
		//savestate
        if (supports_html5_storage()) {
            MoxieFlyout.storage.setItem("MoxieFlyout.isOpen", true);
            MoxieFlyout.storage.setItem("MoxieFlyout.portal", MoxieFlyout.portalId);
            MoxieFlyout.storage.setItem("MoxieFlyout.style", MoxieFlyout.portalStyle);
            MoxieFlyout.storage.setItem("MoxieFlyout.quest", MoxieFlyout.portalQuestionnaire);
		}
	},
    open2: function () {
        if (MoxieFlyout.fullscreen) {
		    var fly = document.getElementById('MoxieFlyoutHolder');
            if (fly != null) {
                MoxieFlyout.addClass(fly, 'MoxieFlyoutFullscreen');
                MoxieFlyout.removeClass(fly, 'MoxieFlyoutToFull');
            } else if (console != null) {
				console.log("Unable to fullscreen MoxieFlyoutPanel");
			}
			MoxieFlyout.resizeFlyoutContent();
		}
        else {
            MoxieFlyout.onResize();
        }
	},
    close: function () {
	    var fly = document.getElementById('MoxieFlyoutHolder');
        if (fly != null) {
            if (!MoxieFlyout.hasClass(fly, 'MoxieFlyoutOpen'))
				return;

			if (MoxieFlyout.fullscreen) {
				MoxieFlyout.hostPage.restore();
				MoxieFlyout.addClass(fly, 'MoxieFlyoutToFull');
			}

            MoxieFlyout.removeClass(fly, 'MoxieFlyoutFullscreen');
			MoxieFlyout.removeClass(fly, 'MoxieFlyoutOpen');
			MoxieFlyout.addClass(fly, 'MoxieFlyoutClosing');
			setTimeout(MoxieFlyout.close2, MoxieFlyout.LONG_DELAY);
        } else if (console != null) {
			console.log("Unable to show MoxieFlyoutPanel");
		}

		MoxieFlyout.hideOnNextPage();
	},
    close2: function () {
	    var fly = document.getElementById('MoxieFlyoutHolder');
		if (fly != null) {
		    MoxieFlyout.removeClass(fly, 'MoxieFlyoutToFull');
		    MoxieFlyout.removeClass(fly, 'MoxieFlyoutClosing');
        } else if (console != null) {
			console.log("Unable to hide MoxieFlyoutPanel");
		}
	},
    hideOnNextPage: function () {
		//save state
		if (supports_html5_storage()) {
            MoxieFlyout.storage.setItem("MoxieFlyout.isOpen", false);
		}
	},
	isOpen: function() {
		var fly = document.getElementById('MoxieFlyoutHolder');
		if (fly != null) {
			return MoxieFlyout.hasClass(fly, 'MoxieFlyoutOpen');
		}
		return false;
	},
    setFlyoutTabText: function (text) {
        document.getElementById('MoxieFlyoutTabText').innerHTML = '<a href="#">' + text + '</a>';
        document.getElementById('MoxieFlyoutTabIcon').alt = text;
        MoxieFlyout.storage.setItem("MoxieFlyout.tabText", text);
	},
    setFlyoutTitleText: function (text) {
		document.getElementById('MoxieFlyoutTitleText').innerHTML = text;
	},
	// Sets text for button with given id
	// 'btnParams.message' will be sent via postMessage when button is clicked
	setFlyoutBtn: function(btnParams) {
		var btnId = btnParams.id;
		var ele = document.getElementById(btnId);

		if (btnId == "ChatWindowDisposalForAgent") {
			disposeOfMoxieFlyoutWindow();
			return;
		}
		if (!ele) return;

		//null text disables / hides the button
		//if message is specified, it is posted as a window message when button is clicked
		var bText = btnParams.text;
		if (bText) {
			ele.innerHTML = bText;
			ele.title = btnParams.title;
			ele.accessKey = btnParams.accessKey;
			ele.style.display = "block";
			MoxieFlyout[btnId + "Message"] = btnParams.message;
		} else {
			ele.innerHTML = "";
			ele.style.display = "none";
			MoxieFlyout[btnId + "Message"] = null;
		}
	},
	setFlyoutContent: function (url, saveURL) {
		// Show error if landscape-mode in certain conditions
		MoxieFlyout.blockOnLandscape();

		if (typeof saveURL === "undefined") {
			saveURL = true;
		}
		var iframe = document.getElementById('MoxieFlyoutIframe');

		if (iframe && iframe.src) {
			// If no sessionStorage, load iframe with html instead of a url
			if (url == "ERROR") {
				iframe.contentWindow.document.write(MoxieFlyout.html_noSessionStorage);
			} else {
				iframe.src = url;
			}
        } else if (console) {
			console.log("Unable to get MoxieFlyoutIframe");
		}
		if (saveURL) {
			MoxieFlyout.setUrl(url);
		}
		MoxieFlyout.openUrl = null;
	},
	setFlyoutContentUponOpen: function(url) {
		if (MoxieFlyout.isOpen()) {
			MoxieFlyout.setFlyoutContent(url);
		} else {
			MoxieFlyout.openUrl = url;
		}
	},
    setUrl: function (url) {
        if (supports_html5_storage()) {
            MoxieFlyout.storage.setItem("MoxieFlyout.content", url);
		}
	},
    setAlert: function (color) {
	    //calling this with null will clear the alert
	    if (supports_html5_storage()) 
            MoxieFlyout.storage.removeItem("MoxieFlyout.alert");
		var ele = document.getElementById('MoxieFlyoutTabAlert');
        if (ele != null) {
            if (color == null) {
			    ele.style.display = 'none';
			} else {
				if (!MoxieFlyout.isOpen()) {
					ele.style.display = 'block';
					ele.style.background = color;
					ele.style.color = color; //this should cause the box-shadow to inherit this color, which is what we are trying to set.

					if (supports_html5_storage())
                        MoxieFlyout.storage.setItem("MoxieFlyout.alert", color);
				}
			}
        } else if (console != null) {
			console.log("Unable to get MoxieFlyoutIframe");
		}
	},
    setChatInProgress: function (sessionID) {
		if (supports_html5_storage()) {
			MoxieFlyout.storage.tabInfo.sessionId = sessionID; //set session id in orig data immediatly, so questionnaire, can clear previous session id, so new session starts correctly

			if (sessionID > 0) {
                MoxieFlyout.storage.setItem("MoxieFlyout.chatInProgress", sessionID);
            } else if (sessionID == 0) {
                MoxieFlyout.storage.removeItem("MoxieFlyout.chatInProgress");
                MoxieFlyout.storage.removeItem("MoxieFlyout.alert");
			} else {
                MoxieFlyout.storage.setItem("MoxieFlyout.chatInProgress", sessionID);
                MoxieFlyout.storage.removeItem("MoxieFlyout.alert");
			}
		} else {
			console.log("sessionStorage not supported - can't save ChatInProgress");
		}
	},
	showPortalQuestionnaire: function () {
	    var portalid = MoxieFlyout.portalId;
		if (supports_html5_storage()) {
            MoxieFlyout.storage.removeItem("MoxieFlyout.chatInProgress");
            MoxieFlyout.storage.removeItem("MoxieFlyout.alert");
            portalid = MoxieFlyout.storage.getItem("MoxieFlyout.portal");
		}

	    //determine if new portal is a flyout portal, and only use it's settings if it is
		var desiredPortal = MoxieGetPortalSettings(MoxieFlyout.newChatPortalId, MoxieFlyout.deviceType);
		if (desiredPortal.tabOrButton != "tab") {
		    //not a flyout portal, just reuse the existing portal
		    MoxieFlyout.portalId = portalid;
		    desiredPortal = MoxieGetPortalSettings(MoxieFlyout.portalId, MoxieFlyout.deviceType);
		    MoxieFlyout.openUrl = MoxieGenerateQuestionnaireUrl(desiredPortal, MoxieGenerateUrlFront(desiredPortal)) + "&flyout=1&fullScreen=" + MoxieFlyout.fullscreen;

		} else {
		    MoxieFlyout.openUrl = MoxieFlyout.portalUrl;
		    MoxieFlyout.portalId = MoxieFlyout.newChatPortalId;
		    MoxieFlyout.portalStyle = MoxieFlyout.newChatPortalStyle;
		    MoxieFlyout.portalQuestionnaire = MoxieFlyout.newCHatQuestionnaire;
		}

		var samePortal = (MoxieFlyout.portalId == portalid);

		//reset all settings from new portal
		MoxieFlyout.startOpen = "";
		var selectedDevice = desiredPortal.selectedDevice;
		var side = MoxieFlyout.RIGHT;
		switch (desiredPortal.tabLocation) {
			case 't': side = MoxieFlyout.TOP; break;
			case 'b': side = MoxieFlyout.BOTTOM; break;
			case 'l': side = MoxieFlyout.LEFT; break;
			case 'r': side = MoxieFlyout.RIGHT; break;
		}
		MoxieFlyout.side = side;
		MoxieFlyout.offset = desiredPortal.tabSideOffset;
		MoxieFlyout.color = selectedDevice.tabBgColor;
		MoxieFlyout.text = selectedDevice.tabText;
		MoxieFlyout.textColor = selectedDevice.tabTextColor;
		MoxieFlyout.openWidth = desiredPortal.newwindowwidth + "px";
		MoxieFlyout.openHeight = desiredPortal.newwindowheight + "px";
		//MoxieFlyout.fullscreen = params.isFullscreen;//skipping setting fullscreen as it was already set correctly for the device
		MoxieFlyout.backColor = selectedDevice.flyOutBgColor;
		MoxieFlyout.titleColor = selectedDevice.titleBgColor;
		MoxieFlyout.titleTextColor = selectedDevice.titleTextColor;
		MoxieFlyout.btnColor = selectedDevice.titleBgColor;
		MoxieFlyout.tabFont = selectedDevice.tabFont;
		MoxieFlyout.titleFont = selectedDevice.tabFont;

		MoxieFlyout.setSettings(samePortal);

		//re-write CSS and html
		var cssp = MoxieFlyout.parse(MoxieFlyout.css);
		var htmltp = MoxieFlyout.parse(MoxieFlyout.htmltab);
		var htmlpp = MoxieFlyout.parse(MoxieFlyout.htmlpanel);

		//inject into page
		var style = document.getElementById("MoxieFlyoutStyle");
		if (style) {
			style.innerHTML = cssp;
		}
		var ele = document.getElementById("MoxieFlyoutHolder");
		if (ele) {
		    ele.className = MoxieFlyout.tabClass;
		        ele.innerHTML = htmltp + htmlpp;
		    }

		MoxieFlyout.setFlyoutBtn({
			id: "MoxieFlyoutBtn1",
			text: selectedDevice.hideText,
			accessKey: "h",
			title: selectedDevice.hideText
		});

		if (samePortal) {
			MoxieFlyout.hostPage.alter();
			if (MoxieFlyout.openUrl) {
				MoxieFlyout.setFlyoutContent(MoxieFlyout.openUrl);
				MoxieFlyout.openUrl = null;
			}
			//savestate
            if (supports_html5_storage()) {
                MoxieFlyout.storage.setItem("MoxieFlyout.isOpen", true);
                MoxieFlyout.storage.setItem("MoxieFlyout.portal", MoxieFlyout.portalId);
                MoxieFlyout.storage.setItem("MoxieFlyout.style", MoxieFlyout.portalStyle);
                MoxieFlyout.storage.setItem("MoxieFlyout.quest", MoxieFlyout.portalQuestionnaire);
			}
		} else {
			MoxieFlyout.open();
		}
	},
	btnClick: function(btnElem) {
		var msgToPost = MoxieFlyout[btnElem.id + "Message"];
		if (msgToPost) {
			MoxieFlyout.sendFlyoutMessage(msgToPost, 0);
		}
	},
	openSurvey: function (surveyUrl) {
	    var bgClrReg = /rgba?\((\d+)\s?,\s?(\d+)\s?,\s?(\d+)/;
	    var regMatches = MoxieFlyout.backColor.match(bgClrReg);
	    var logoColorIndex = 0;

	    if (regMatches.length >= 4) {
	        var bgColor = parseInt((regMatches[1] * 299 + regMatches[2] * 587 + regMatches[3] * 114) / 1000)
	        logoColorIndex = (bgColor < 125) ? 1 : 0;
	        surveyUrl += '&logocoloridx=' + logoColorIndex;
	    }
	    MoxieFlyout.setFlyoutContent(surveyUrl, false);
        document.getElementById('MoxieFlyoutIframe').focus();
	},
	setReturnFromSurvey: function () {
		if (supports_html5_storage()) {
            MoxieFlyout.storage.setItem("MoxieFlyout.returnFromSurvey", true);
		}
	},
	checkReturnFromSurvey: function () {
		if (supports_html5_storage()) {
            var isReturningFromSurvey = MoxieFlyout.storage.getItem("MoxieFlyout.returnFromSurvey");
			if (isReturningFromSurvey) {
                MoxieFlyout.storage.removeItem("MoxieFlyout.returnFromSurvey");
				MoxieFlyout.close();
			}
		}
	},
	chatFocus: function (elementOffset) {
		if (MoxieFlyout.deviceType == 2) {//"tablet";
			setTimeout(function () {
				var holder = document.getElementById("MoxieFlyoutHolder");
				var pannel = document.getElementById("MoxieFlyoutPanel");
				var dimensions = MoxieFlyout.getWindowDimensions();
				var flyoutHeight = 0;
				if (MoxieFlyout.openHeight.indexOf("px") > 0) {
					flyoutHeight = parseInt(MoxieFlyout.openHeight);
				} else if (MoxieFlyout.openHeight.indexOf("%") > 0) {
					flyoutHeight = dimensions.height * (parseInt(MoxieFlyout.openHeight) / 100);
				}
				var elementOffsetNum = 0;
				if (elementOffset) { //coming from questionnaire
					elementOffsetNum = parseInt(elementOffset);
				}

				if (MoxieFlyout.iOSVersion().major == 8 && MoxieFlyout.isSafari) { //safari on ios 8
					var offsetNum = 0;
					if (dimensions.orientation == "portrait") {
						offsetNum = dimensions.height * MoxieFlyout.offset / 100;
					} else {
						if (elementOffsetNum) {
							flyoutHeight = elementOffsetNum;
						}
						offsetNum = (dimensions.height * 0.3) - flyoutHeight;
					}
					offsetNum = offsetNum + window.pageYOffset;
					var offset = offsetNum + "px";

					holder.style.top = offset;
					pannel.style.top = offset;
				} else if (!MoxieFlyout.iOSVersion().major) { //non-ios tablet
					var availableHeight = (dimensions.orientation == "portrait") ? 0.9 : 0.6; //less space for landscape
					setTimeout(function () {
						dimensions = MoxieFlyout.getWindowDimensions();
						if (elementOffsetNum) {
							if (!MoxieFlyout.isVisible(elementOffsetNum, dimensions.height * availableHeight)) {
								flyoutHeight = elementOffsetNum;
							} else {
								return;
							}
				}
						var offset = dimensions.height * availableHeight - flyoutHeight + "px";
				holder.style.top = offset;
				pannel.style.top = offset;
					}, MoxieFlyout.LONG_DELAY / 2);
				}
			}, 2 * MoxieFlyout.SHORT_DELAY);
		}
	},
	chatBlur: function () {
		if (MoxieFlyout.deviceType == 2) {
			var ua = navigator.userAgent;
			var isSafari = (ua.match("Safari") && !(ua.match("CriOS") || ua.match("Chrome")));
			var holder = document.getElementById("MoxieFlyoutHolder");
			var pannel = document.getElementById("MoxieFlyoutPanel");
			if (MoxieFlyout.iOSVersion().major == 8 && isSafari) { //"tablet";
			switch (parseInt(MoxieFlyout.side)) {
				case MoxieFlyout.TOP: 
				case MoxieFlyout.BOTTOM: {
					holder.style.top = "";
					pannel.style.top = "";
				}
					break;
				case MoxieFlyout.LEFT:
				case MoxieFlyout.RIGHT:
				default: {
					var offset = MoxieFlyout.getWindowDimensions().height * MoxieFlyout.offset / 100; //Calculate pixel equivalent of percentage offset

					holder.style.top = offset + "px";
					pannel.style.top = offset + "px";
				}
				}
			} else if (!MoxieFlyout.iOSVersion().major) { //non-ios tablet
				holder.style.top = "";
				pannel.style.top = "";
			}
		}
	},
	isVisible: function(elementOffset, screenHeight) {
		var visible = false;
		switch (parseInt(MoxieFlyout.side)) {
			case MoxieFlyout.TOP: {
				visible = elementOffset < screenHeight;
				break;
			}
			case MoxieFlyout.BOTTOM: {
				var flyoutHeight = 0;
				if (MoxieFlyout.openHeight.indexOf("px") > 0) {
					flyoutHeight = parseInt(MoxieFlyout.openHeight);
				} else if (MoxieFlyout.openHeight.indexOf("%") > 0) {
					flyoutHeight = dimensions.height * (parseInt(MoxieFlyout.openHeight) / 100);
			}
				visible = flyoutHeight - elementOffset < screenHeight;
				break;
		}
			case MoxieFlyout.LEFT:
			case MoxieFlyout.RIGHT:
			default: {
				var offset = screenHeight * MoxieFlyout.offset / 100; //Calculate pixel equivalent of percentage offset
				visible = elementOffset + offset < screenHeight;
			}
		}
		return visible;
	},
    processMessage: function (msg) {
		//processes messages from other windows - handles ones it understands
		var obj = null;
		if (Object.prototype.toString.call(msg.data) == '[object String]') {
		    try {
		        //not parsed yet
                if (window.JSON) {
		            //built in parser
		            obj = JSON.parse(msg.data);
                } else {
		            //use a library
		            obj = jsonParse(msg.data);
		        }
		    } catch (err) {
                // Don't act if the string is not valid JSON
		    }
        } else {
			obj = msg.data;
		}

		if (!obj) return;

		switch (obj.call) {
			case "open":
				MoxieFlyout.open();
				break;
			case "close":
				MoxieFlyout.close();
				break;
			case "setFlyoutTabText":
				MoxieFlyout.setFlyoutTabText(obj.text);
				break;
			case "setFlyoutTitleText":
				MoxieFlyout.setFlyoutTitleText(obj.text);
				break;
			case "setFlyoutBtn":
				MoxieFlyout.setFlyoutBtn(obj);
				break;
			case "setFlyoutContent":
				MoxieFlyout.setFlyoutContent(obj.url, obj.saveURL);
				break;
			case "setFlyoutContentUponOpen":
				MoxieFlyout.setFlyoutContentUponOpen(obj.url);
				break;
			case "setUrl":
				MoxieFlyout.setUrl(obj.url);
				break;
			case "setAlert":
				MoxieFlyout.setAlert(obj.color);
				break;
			case "setChatInProgress":
				MoxieFlyout.setChatInProgress(obj.sessionId);
				break;
			case "hideOnNextPage":
				MoxieFlyout.hideOnNextPage();
				break;
			case "showPortalQuestionnaire":
				MoxieFlyout.showPortalQuestionnaire();
				break;
		    case "openSurvey":
		        MoxieFlyout.openSurvey(obj.url);
		        break;
			case "setReturnFromSurvey":
				MoxieFlyout.setReturnFromSurvey();
				break;
			case "checkReturnFromSurvey":
				MoxieFlyout.checkReturnFromSurvey();
				break;
		    case "openWindow":
		        MoxieFlyout.openWindow(obj.url, obj.target);
		        break;
		    case "resize":
		        MoxieFlyout.onResize();
		        break;
			case "chatFocus":
				MoxieFlyout.chatFocus(obj.offset);
				break;
			case "chatBlur":
				MoxieFlyout.chatBlur();
				break;
			case "scrollBy":
				window.scrollBy(obj.x, obj.y);
                break;
            case "getTabInfo":
		let flyoutHolderRef2 = document.getElementById("MoxieFlyoutHolder");
		if (flyoutHolderRef2) {
			flyoutHolderRef2.style.display='block';
		}
		var myTabInfo = MoxieFlyout.storage.getTabInfo();

		if (window.talCustProp)
		{
			try {
				var authUser = window.talCustProp.match(/MXUser\=(.*?)(\#\:Prop\!|$)/i);
				if (authUser) {
					myTabInfo.authUser = authUser[1];
				}
				
				var authEmail = window.talCustProp.match(/MXEmail\=(.*?)(\#\:Prop\!|$)/i);
				if (authEmail) {
					myTabInfo.authEmail = authEmail[1];
				}

				var authLang = window.talCustProp.match(/MXLanguage\=(.*?)(\#\:Prop\!|$)/i);
				if (authLang) {
					myTabInfo.authLang = authLang[1];
				}
			}
			catch(err) {
				//TODO Log errors
			}
		}  

                MoxieFlyout.sendFlyoutMessage(JSON.stringify(myTabInfo), 0);
            	// After tabInfo is consumed, we need to refresh it by setting previous origin to current origin.
				// That way when client get the data again from hosted page, we can use session storage.
                if (!MoxieFlyout.isTabInfoRequestOccured) {
            		MoxieFlyout.storage.refresh();
            		MoxieFlyout.isTabInfoRequestOccured = true;
				}
            	break;
			case "setSessionTimeout":
				MoxieFlyout.storage.setItem("MoxieFlyout.sessionTimeout", obj.sessionTimeout);
				break;
		}
	},
    parse: function (str) {
		str = str.replace(/%offset%/g, MoxieFlyout.offset);
		str = str.replace(/%color%/g, MoxieFlyout.color);
        str = str.replace(/%text%/g, MoxieFlyout.text.replace(/"/g, '&quot;'));
		str = str.replace(/%textColor%/g, MoxieFlyout.textColor);
		str = str.replace(/%width%/g, MoxieFlyout.openWidth);
		str = str.replace(/%height%/g, MoxieFlyout.openHeight);
		str = str.replace(/%backColor%/g, MoxieFlyout.backColor);
		str = str.replace(/%titleColor%/g, MoxieFlyout.titleColor);
		str = str.replace(/%titleTextColor%/g, MoxieFlyout.titleTextColor);
		str = str.replace(/%btnColor%/g, MoxieFlyout.btnColor);
		str = str.replace(/%btn1text%/g, MoxieFlyout.btn1Text);
		str = str.replace(/%btn2text%/g, MoxieFlyout.btn2Text);
		str = str.replace(/%tabFont%/g, MoxieFlyout.tabFont);
		str = str.replace(/%titleFont%/g, MoxieFlyout.titleFont);
		str = str.replace(/%serverUrl%/g, MoxieFlyout.serverUrl);
		
		str = str.replace(/%class%/g, MoxieFlyout.tabClass);
		str = str.replace(/%open%/g, MoxieFlyout.startOpen);
		return str;
	},
	
    addClass: function (ele, clName) {
        if (ele.classList != null) {
			ele.classList.add(clName);
        } else {
            ele.className += (ele.className ? ' ' : '') + clName;
		}
	},

    removeClass: function (ele, clName) {
        if (ele.classList != null) {
			ele.classList.remove(clName);
        } else {
            ele.className = ele.className.replace(new RegExp('(\\s|^)' + clName + '(\\s|$)', "g"), ' ');
		}
	},

    hasClass: function (ele, clName) {
        if (ele.classList != null) {
			return ele.classList.contains(clName);
        } else {
            return ele.className.match(new RegExp('(\\s|^)' + clName + '(\\s|$)'));
		}
	},

	// Manage host page layout so it can be changed as flyout opens/closes
	hostPage: (function() {
		// Values to compensate for frame border when setting position or scroll value
		var yDelta = 0;
		var xDelta = 0;
		var frameHolder = document.getElementById("MoxieFlyoutFrameHolder");
		if (frameHolder) {
			yDelta = (parseInt(frameHolder.style.borderTop) + parseInt(frameHolder.style.borderBottom)) || 0;
			xDelta = (parseInt(frameHolder.style.borderLeft) + parseInt(frameHolder.style.borderRight)) || 0;
		}

		// Restore host page
		function restore() {
			if (MoxieFlyout.fullscreen) {
				var scrollY = Math.abs(parseInt(document.body.style.top) + yDelta);
				var scrollX = Math.abs(parseInt(document.body.style.left) + xDelta);
				this.origValues.restoreAll();
                window.scrollTo(scrollX, scrollY);
			}
		}

		function alter() {
			// Change host page while flyout open
			if (MoxieFlyout.fullscreen) {
				// Prevent body from scrolling as well as absolute-positioned element heights
				// from contributing to document height while keyboard open
				var doc = document.documentElement;
				var b = document.body;
				this.origValues.save(b, "attribute", "class");
				this.origValues.save(b, "style", "top");
				this.origValues.save(b, "style", "left");

				// Position page so it looks same despite being fixed
				b.style.top = -(parseInt((window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0)) - yDelta) + "px";
                b.style.left = -(parseInt((window.pageXOffset || doc.scrollLeft) - (doc.clientLeft || 0)) - xDelta) + "px";
				MoxieFlyout.addClass(b, "fixed");
			}
		}

		// Saves a DOM element property so it can be restored later.
		var origValues = (function() {
			// sample structure:
			// savedObjects = {
			//  domId1: [simple array of objects]
			//  domId2: // sample
			//	domId2[0] = {propertyType: "attribute", propertyName: "class", propertyValue: "someClass"}
			//	domId2[1] = {propertyType: "style", propertyName: "color", propertyValue: "blue"}
			// }
			var savedObjects = {};
			var newId = 0;

			// @elem: A DOM element.
			// @propertyType: "attribute", "style".
			// @propertyName: attribute or style name.
			function save(elem, propertyType, propertyName) {
				// Do nothing if element invalid
				if (elem) {
					// Give the element an id if it doesn't have one
					if (elem.id !== "0" && !elem.id) {
						elem.id = "moxie-temp-" + newId++;
					}

					if (!savedObjects[elem.id]) {
						savedObjects[elem.id] = [];
					}

					// What value to save
					var valueToSave = (propertyType == "attribute") ?
						(elem.getAttribute(propertyName) || "") : // default to empty-string
						elem.style[propertyName];

					// Save the value
					savedObjects[elem.id].push({
						propertyType: propertyType,
						propertyName: propertyName,
						propertyValue: valueToSave
					});
				}
			}
			// Restores each saved DOM element's saved property to its original value.
			// Elements that do not currently exist are ignored.
			function restoreAll() {
				var key;

				for (key in savedObjects) {
					if (savedObjects.hasOwnProperty(key)) {
						var curObj = savedObjects[key];
						var curElem = document.getElementById(key);

						// Ignore currently invalid elements
						if (curElem) {
							for (var i = 0; i < curObj.length; i++) {
								var curPropertyName = curObj[i].propertyName;
								var curPropertyValue = curObj[i].propertyValue;

								if (curObj[i].propertyType == "attribute") {
									curElem.setAttribute(curPropertyName, curPropertyValue);
								} else {
									curElem.style[curPropertyName] = curPropertyValue;
								}
							}
						}
						// Mark object for gc
						savedObjects.key = null;
					}
				}
			}
			return {
				save: save,
				restoreAll: restoreAll,
			}
		})()

		return {
			alter: alter,
			restore: restore,
			origValues: origValues
		}
	})(),

	onResize: function () {
		var resizeWork = function () {
			var height;
			var width;
			if (document.documentElement && document.documentElement.clientWidth) {
				//this excludes the space scrollbars take up
				width = document.documentElement.clientWidth;
				height = document.documentElement.clientHeight;
			} else {
				//this will include scrollbar size, so we actually have a bit less room than this
				width = window.innerWidth;
				height = window.innerHeight
			}

			switch (parseInt(MoxieFlyout.side)) {
				case MoxieFlyout.TOP: {
					if (!MoxieFlyout.fullscreen)
						MoxieFlyout.offset = MoxieFlyout.calcOffest(MoxieFlyout.offset, MoxieFlyout.openWidth, width);
				}
					break;
				case MoxieFlyout.BOTTOM: {
					if (!MoxieFlyout.fullscreen)
						MoxieFlyout.offset = MoxieFlyout.calcOffest(MoxieFlyout.offset, MoxieFlyout.openWidth, width);
				}
					break;
				case MoxieFlyout.LEFT: {
					if (!MoxieFlyout.fullscreen)
						MoxieFlyout.offset = MoxieFlyout.calcOffest(MoxieFlyout.offset, MoxieFlyout.openHeight, height);
				}
					break;
				case MoxieFlyout.RIGHT:
				default: {
					if (!MoxieFlyout.fullscreen)
						MoxieFlyout.offset = MoxieFlyout.calcOffest(MoxieFlyout.offset, MoxieFlyout.openHeight, height);
				}
			}
			var cssp = MoxieFlyout.parse(MoxieFlyout.css);
			//inject into page
			var style = document.getElementById("MoxieFlyoutStyle");
			if (style) {
				style.innerHTML = cssp;
			}

			// Update the DOM to force mobile-browsers to reflow the page
			// since mobile browsers don't reliably do it for iframed-content

			// determine current orientation
			var dimensions = MoxieFlyout.getWindowDimensions();
			var orientation = dimensions.orientation;

			var portraitValue = "width=device-width";
			var landscapeValue = "width=device-height";
			var viewportElems = document.querySelectorAll("meta[name='viewport']");

			// rewrite viewport tags based on current orientation
			for (var i = 0; i < viewportElems.length; i++) {
				var viewportElem = viewportElems[i];

				if (orientation == "portrait") {
					viewportElem.content = viewportElem.content.replace(landscapeValue, portraitValue);
				} else {
					viewportElem.content = viewportElem.content.replace(portraitValue, landscapeValue);
				}
			}

			// collapse keyboard
			document.activeElement && document.activeElement.blur();
			MoxieFlyout.chatBlur(); //recalculate pixel position on orientation change

			// allow doc to scroll
            var fixed = MoxieFlyout.hasClass(document.body, "fixed");
			MoxieFlyout.removeClass(document.body, "fixed");

			setTimeout(function() { // Allow time for keyboard collapse
				// Force DOM-refresh
				var t = document.createElement('div');
				t.id = "_temp_";
				t.style.position = "absolute;";
				document.body.appendChild(t);
				setTimeout(function() { // Allow time for DOM-refresh
					document.body.removeChild(t);
					if (fixed) {
						MoxieFlyout.addClass(document.body, "fixed");
					}

					if (!MoxieFlyout.blockOnLandscape()) {
						window.scrollTo(0, 0);
					}

					// Inform flyout content-page of the current document size
					MoxieFlyout.resizeFlyoutContent();
                }, 2 * MoxieFlyout.SHORT_DELAY);
			}, 2 * MoxieFlyout.SHORT_DELAY);
		};
		// If it's iPad with iOS 7 running Safari, we need to give it half a second for DOM to update it's dimention
		// to the new oritentation.
		if (MoxieFlyout.deviceType == 2 && MoxieFlyout.iOSVersion().major == 7 && MoxieFlyout.isSafari) {
			setTimeout(function () {
				// This will fix the extra black and gray area at the bottom of the page on orientation change
				// with keyboard shown.
				window.scrollTo(window.pageXOffset, window.pageYOffset);
				resizeWork();
			}, MoxieFlyout.LONG_DELAY / 2);
		}
		else // Otherwise, just do resize work that we used to do.
			resizeWork();
	},
	setIframeFocus: function() {
		// When a textbox has focus and keyboard open, if the textbox loses focus then the keyboard
		// remains open but no characters appear while tapping (because main window has focus).
		setTimeout(function() {
			if (MoxieFlyout.isOpen && window.document.activeElement && window.document.activeElement.tagName == "BODY") {
				window.frames["MoxieFlyoutIframe"].focus();
			}
		}, 0);
	},
	// Send message to iframe window using window.postMessage
	// @msg: String to post to iframe window
	// @delay: Time in ms to delay the message
	sendFlyoutMessage: function(msg, delay) {
		var ifr = document.getElementById("MoxieFlyoutIframe");
		var ifrWindow = (ifr.contentWindow || ifr);
		if (delay > 0) {
			setTimeout(function() { // Allow time for window to resize
				ifrWindow.postMessage(msg, "*");
			}, delay);
		} else {
			ifrWindow.postMessage(msg, "*");
		}
	},
	openWindow: function (url, target) {
	    setTimeout(function () {
	        window.open(url, target);
		}, MoxieFlyout.LONG_DELAY);
	},
	resizeFlyoutContent: function() {
		var dimensions = MoxieFlyout.getWindowDimensions();

		// Tell flyout content page to resize its contents
		var flyoutTitle = document.getElementById("MoxieFlyoutTitle");
		var textRect = flyoutTitle.getBoundingClientRect();
		var msg = {
			message: "setDocumentSize",
			width: dimensions.width,
			height: dimensions.height - (textRect.bottom - textRect.top), // window height minus titlebar height
			orientation: dimensions.orientation
		};
		MoxieFlyout.sendFlyoutMessage(JSON.stringify(msg), MoxieFlyout.SHORT_DELAY);
	},
	getWindowDimensions: function() {
		var w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
		var h = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
		if (typeof MoxieFlyout.initialDimensions == "undefined") {
			MoxieFlyout.initialDimensions = {
				width: w,
				height: h,
				orientation: w > h ? "landscape" : "portrait"
			}
			return MoxieFlyout.initialDimensions;
		}
		var currentOrientation = "";
		currentOrientation = w > h ? "landscape" : "portrait";
		return {
			width: w,
			height: h,
			orientation: currentOrientation
		}
	},
	iOSVersion: function() {
		var obj = {
			major: NaN,
			minor: NaN,
			build: NaN
		};
		if (navigator.platform.match(/(iPad|iPhone|iPod)/i)) {
			// supports iOS 2.0 and later: <https://bit.ly/TJjs1V>
			var version = (navigator.appVersion).match(/OS (\d+)_(\d+)_?(\d+)?/i);
			if (version && version[1]) {
				obj.major = parseInt(version[1], 10),
				obj.minor = parseInt(version[2] || 0, 10),
				obj.build = parseInt(version[3] || 0, 10)
			}
		}
		return obj;
	},
	isSafariBrowser: function () {
		return (navigator.userAgent.match("Safari") && !(navigator.userAgent.match("CriOS") || navigator.userAgent.match("Chrome")));
	},
	blockOnLandscape: function() {
		var errorMsg = "";
		if (MoxieFlyout.fullscreen && MoxieFlyout.getWindowDimensions().orientation == "landscape") {
			// <= iOS 7 + Safari:
			// Show error message when switched to landscape because touching screen top or bottom causes address-bar/navigation-bar to redraw screen,

			// but displayed elements no longer match DOM, thereby causing page controls to not respond.
			if (MoxieFlyout.iOSVersion().major <= 7 && MoxieFlyout.isSafari) {
				errorMsg = "Please switch to portrait mode";
			}
		}
		var errorCover = document.getElementById("ErrorCover");
		errorCover.innerHTML = errorMsg;
		errorCover.style.display = errorMsg ? "block" : "none";

		return (errorMsg == "");
	},
	// Append or modify an existing query string value for a specified URL.
	addQueryStringToUrl: function (url, queryStringType, getValueCallback) {
		if (!url || 0 >= url.length || !queryStringType)
			return url;

		var newUrl = url;
		var newValue;

		if (getValueCallback)
			newValue = getValueCallback();

		switch (queryStringType) {
			case MoxieFlyout.queryStringType.FullScreen: {
				if (!getValueCallback)
					newValue = (DetectAndroidPhone() || DetectIphoneOrIpod() || DetectWindowsPhone7());

				var fullScreenQueryString = "fullScreen=" + newValue;

				var match = url.match(/fullScreen=(true|false)/i);
				if (match) {
					newUrl = newUrl.replace(match[0], fullScreenQueryString);
				}
				else {
					newUrl += (0 <= newUrl.indexOf("?") ? "&" : "?");
					newUrl += fullScreenQueryString;
				}
				break;
			}
		}

		return newUrl;
    },

    //determines if an object is a function
    isFunction: function (propToTest) {
        var getType = {};
        return propToTest && getType.toString.call(propToTest) === '[object Function]';
    },

    //Basic 'localStorage' replacement object.  Not meant to be used. Use one of the subclasses, StorageSessionStorage, StorageCookie, StorageMixed.
    //Implements 'localStorage' like interface but allows data to be stored in a different way.
    StorageBase: function () {
        //interanl functions

        //base object
        var obj = {
            storageInited: false,
            storageTag: "MoxieFlyout.",
            store: {}, //actual object storing the data
            tabInfo: null //copy of data that Client needs as it was originally read out of storage mechanism
        };
        //should be called by subclasses when done reading data to mark as initialized
        // @tabData: the data from window.name
        obj.inited = function(tabData) {
            tabData = tabData || {};
            obj.tabInfo = {
                cookieID: tabData.cookieID || Math.ceil(Math.random() * 100000),
                origWindowName: tabData.origWindowName || window.name,
                currentOrigin: tabData.currentOrigin || window.location.protocol + window.location.host, //window.location.origin; not supported in IE below 11
                previousOrigin: tabData.previousOrigin || window.location.protocol + window.location.host,
                sessionId: tabData.sessionId || obj.getItem("MoxieFlyout.chatInProgress") || 0
            };
            obj.storageInited = true;
        };
        //returns tabInfo
        obj.getTabInfo = function() {
            return obj.tabInfo;
        };
        //intended to be overridden in subclasses.
        obj.read = function () {
            obj.storageInited = true;
        };
        //intended to be overridden in subclasses.
        obj.write = function () { };

        //external functions

        //Returns the value associated with 'name', if any
        // @name: the name of the value to return the stored value of
        obj.getItem = function (name) {
            if (!obj.storageInited) {
                this.read();
            }
            if (obj.store.hasOwnProperty(name) && !MoxieFlyout.isFunction(obj.store[name])) {
                return obj.store[name];
            }
            return null;
        };
        //Stores a name value pair
        // @name: the name of the value to store
        // @value: the value to associate with the name
        obj.setItem = function (name, value) {
            obj.store[name] = value;
            this.write();
        };
        //Removes the named value from the store
        // @name: the name of the value to remove
        obj.removeItem = function (name) {
            delete obj.store[name];
            this.write();
        };

    	// Updates original data property values
		// Use this in cases where storage needs to be updated BEFORE a pagehide event
        obj.refresh = function () {
            this.tabInfo.previousOrigin = this.tabInfo.currentOrigin;
        };

        return obj;
    }(),

    getCookie: function (n) {
        var c = document.cookie.split("; ");
        for (var i = 0; i < c.length; i++) {
            var ac = c[i].split("=");
            if (n == ac[0]) {
                ac = (ac.splice(1)).join("=");
                return unescape(ac);
            }
        }
        return null;
    },

    setCookie: function (namevalue, expires, path, domain) {
        var thecookiestring = namevalue +
            ((expires) ? "; expires=" + expires : "") +
            ((path) ? "; path=" + path : "") +
            ((domain) ? "; domain=" + domain : "");
        document.cookie = thecookiestring;
    },

    storage: null,
};
};

var MoxieFlyout = MoxieFlyout || MoxieFlyoutReset();

//A storage object that uses session storage as it's backing store (i.e. original flyout functionality using this new interface)
function MySessionStorage() {
    var obj = Object.create(MoxieFlyout.StorageBase);
    obj.read = function () {
        var tagLen = obj.storageTag.length;
        for (i = 0; i < sessionStorage.length; i++) {
            var key = sessionStorage.key(i);
            if (key.substr(0, tagLen) === obj.storageTag) {
                //this is one of our settings, read it
                obj.store[key] = sessionStorage.getItem(key);
            }
        }
        obj.inited();
    };
    obj.write = function () {
        for (prop in obj.store) {
            if (obj.store.hasOwnProperty(prop) && !MoxieFlyout.isFunction(obj.store[prop])) {
                sessionStorage.setItem(prop, obj.store[prop]);
            }
        }
    };
    return obj;
};
MoxieFlyout.StorageSessionStorage = MySessionStorage();

//A storage object that uses a session cookie as it's backing store (works, but all tabs share same data)

function MyCustomCookieStorage () {
    var obj = Object.create(MoxieFlyout.StorageBase);
    obj.cookieName = obj.storageTag + "Cookie";

    //reads the cookie and returns the data as an object 
    obj.getCookieData = function () {
        cookie = MoxieFlyout.getCookie(obj.cookieName);

        var data = null;
        if (cookie != null && cookie.length > 0) {
            try {
                    data = JSON.parse(cookie);
            } catch (err) {} // Don't act if the string is not valid JSON
        }
        return data;
    };
    obj.read = function () {
        var data = obj.getCookieData();

        if (data != null) {
            for (prop in data) {
                if (data.hasOwnProperty(prop) && !MoxieFlyout.isFunction(data[prop])) {
                    obj.store[prop] = data[prop];
                }
            }
        }
        obj.inited();
    };
    obj.write = function() {
        var expires = new Date();
        expires.setTime(expires.getTime() + MoxieFlyout.storage.getItem("MoxieFlyout.sessionTimeout") || 90000);
        obj.store["cExpire"] = expires.valueOf();

        var nameval = obj.cookieName + "=" + JSON.stringify(obj.store);
        var hostName = window.location.hostname;
        var domainname = hostName;

        // If hostname is not an ip, set cookie using root domain
        if (hostName.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/) === null) {
            var hostParts = hostName.split(".");

            // Use last two parts of domain if available, otherwise just use root
            var firstIndex = (hostParts.length > 1) ? -2 : -1;
            domainname = hostParts.slice(firstIndex).join(".");
	}
        MoxieFlyout.setCookie(nameval, expires.toUTCString(), "/", domainname);
};
    obj.delCookie = function () {
        //very similar to write, but no value and date in the past
        var nameval = obj.cookieName + "=";
        var expires = (new Date(0)).toUTCString();
        var hostName = window.location.hostname;
        var domainname = hostName;

        // If hostname is not an ip, set cookie using root domain
        if (hostName.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/) === null) {
            var hostParts = hostName.split(".");

            // Use last two parts of domain if available, otherwise just use root
            var firstIndex = (hostParts.length > 1) ? -2 : -1;
            domainname = hostParts.slice(firstIndex).join(".");
        }
        MoxieFlyout.setCookie(nameval, expires, "/", domainname);
    };
    return obj;
};
MoxieFlyout.StorageCookie = MyCustomCookieStorage();

// A storage object that uses a combination of a cookie and window.name so that each tab is using a different cookie by storing the cookie name in 
// window.name, with some additional code to attempt to preserve any data the host site may be placing in window.name, additionally backing everything up in 
// sessionStorage incase window.name / cookie are unreadable .  Uses some calls to StorageCookie, and StorageSessionStorage.
function MyCustomStorage() {
    var obj = Object.create(MoxieFlyout.StorageBase);
    obj.cookieName = obj.storageTag + "Cookie";

    //real write function that gets called on pagehide/unload
    obj.realWrite = function () {
        window.name = JSON.stringify(obj.getTabInfo());

        //save cookie
        obj.cookieName = obj.storageTag + obj.getTabInfo().cookieID + "Cookie";
        MoxieFlyout.StorageCookie.cookieName = obj.cookieName;
        MoxieFlyout.StorageCookie.store = obj.store;
        MoxieFlyout.StorageCookie.write();

        //backup everything in session storage as well
        MoxieFlyout.StorageSessionStorage.store = obj.store;
        MoxieFlyout.StorageSessionStorage.write();
    };

	// Read a cookie that contains data about flyout state.
	// The cookie name is retrieved from window.name. If unavailable,
	// use most recent cookie with expected name format.
	obj.read = function () {
		// Setup unload
		var unload = function () {
			obj.realWrite();
		}
		var eventName = ("onpagehide" in window) ? "pagehide" : "unload";
		window.addEventListener(eventName, unload);

		var cookieName = null;
		var cookieData = null;
		var recoveredTabInfo = null;
		if (window.name) {
			// Get cookie name from window.name
			try {
				recoveredTabInfo = JSON.parse(window.name);
			} catch (err) {} // Don't act if the string is not valid JSON
		}

		// Determine which cookie contains data used to restore flyout
		if (recoveredTabInfo && recoveredTabInfo.cookieID) {
			// Cookie name provided by window.name
			cookieName = obj.storageTag + recoveredTabInfo.cookieID + "Cookie";
			window.name = recoveredTabInfo.origWindowName;
		} else {
			// Couldn't get cookie name from window.name, so get data from most recent cookie
			var maxExpire = 0;
			var keyValuePairs = document.cookie.split(/; */);
			var re = new RegExp("(" + obj.storageTag + ")(\\d+)(Cookie)"); // e.g. MoxieFlyout.52990Cookie

			// Iterate all cookies
			for (var i = 0; i < keyValuePairs.length; i++) {
				var name = keyValuePairs[i].substring(0, keyValuePairs[i].indexOf('='));

				// Check whether this is a storage cookie
				if (re.test(name)) {
					cookieName = cookieName || name;
					recoveredTabInfo = recoveredTabInfo || {};

					// Test whether this cookie is more recent than others already found
					var value = keyValuePairs[i].substring(keyValuePairs[i].indexOf('=') + 1);
					value = value && JSON.parse(value);
					if (value.cExpire > maxExpire) {
						maxExpire = value.cExpire;
						cookieName = name;
						var parts = name.match(re);
						recoveredTabInfo.cookieID = parts[2];
						recoveredTabInfo.sessionId = value[obj.storageTag + "chatInProgress"] || 0;
				    }
			    }
			}
		}

		obj.cookieName = cookieName;

		// read data from cookie
		if (obj.cookieName) {
			MoxieFlyout.StorageCookie.cookieName = obj.cookieName;
			cookieData = MoxieFlyout.StorageCookie.getCookieData();
			MoxieFlyout.StorageCookie.delCookie();
		}

		// add data to storage
		if (cookieData) {
			for (prop in cookieData) {
				if (cookieData.hasOwnProperty(prop) && !MoxieFlyout.isFunction(cookieData[prop])) {
					obj.store[prop] = cookieData[prop];
				}
			}
		}

		obj.inited(recoveredTabInfo);
}

	return obj;
};
MoxieFlyout.StorageMixed = MyCustomStorage();

//set / change the storage used here - may need to modify supports_html5_storage() as well.
MoxieFlyout.storage = MoxieFlyout.StorageMixed;
//read and reset window.name, hopefully before 'onload' so data is back in place before host page tries to use it (this is assuming StorageMixed is being used)

MoxieFlyout.storage.read();


//https://code.google.com/p/json-sans-eval/
window.jsonParse = function () {
    var r = "(?:-?\\b(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\\b)", k = '(?:[^\\0-\\x08\\x0a-\\x1f"\\\\]|\\\\(?:["/\\\\bfnrt]|u[0-9A-Fa-f]{4}))'; k = '(?:"' + k + '*")'; var s = new RegExp("(?:false|true|null|[\\{\\}\\[\\]]|" + r + "|" + k + ")", "g"), t = new RegExp("\\\\(?:([^u])|u(.{4}))", "g"), u = { '"': '"', "/": "/", "\\": "\\", b: "\u0008", f: "\u000c", n: "\n", r: "\r", t: "\t" }; function v(h, j, e) { return j ? u[j] : String.fromCharCode(parseInt(e, 16)) } var w = new String(""), x = Object.hasOwnProperty; return function (h,

    j) {
        h = h.match(s); var e, c = h[0], l = false; if ("{" === c) e = {}; else if ("[" === c) e = []; else { e = []; l = true } for (var b, d = [e], m = 1 - l, y = h.length; m < y; ++m) {

            c = h[m]; var a; switch (c.charCodeAt(0)) {
                default: a = d[0]; a[b || a.length] = +c; b = void 0; break; case 34: c = c.substring(1, c.length - 1); if (c.indexOf("\\") !== -1) c = c.replace(t, v); a = d[0]; if (!b) if (a instanceof Array) b = a.length; else { b = c || w; break } a[b] = c; b = void 0; break; case 91: a = d[0]; d.unshift(a[b || a.length] = []); b = void 0; break; case 93: d.shift(); break; case 102: a = d[0]; a[b || a.length] = false;

                    b = void 0; break; case 110: a = d[0]; a[b || a.length] = null; b = void 0; break; case 116: a = d[0]; a[b || a.length] = true; b = void 0; break; case 123: a = d[0]; d.unshift(a[b || a.length] = {}); b = void 0; break; case 125: d.shift(); break

            }
        } if (l) { if (d.length !== 1) throw new Error; e = e[0] } else if (d.length) throw new Error; if (j) {
            var p = function (n, o) {
                var f = n[o]; if (f && typeof f === "object") { var i = null; for (var g in f) if (x.call(f, g) && f !== n) { var q = p(f, g); if (q !== void 0) f[g] = q; else { i || (i = []); i.push(g) } } if (i) for (g = i.length; --g >= 0;) delete f[i[g]] } return j.call(n,

                o, f)
            }; e = p({ "": e }, "")
        } return e
    }
}();




if (supports_html5_storage()) {
	var launchIfNoFlyout = function () {
        var inProgress = MoxieFlyout.storage.getItem("MoxieFlyout.chatInProgress");
		if (inProgress && inProgress.length > 0) {
            DetectDevice(MoxieFlyout.storage.getItem("MoxieFlyout.portal"), null, null, null, null);
		}
	};
    setTimeout(launchIfNoFlyout, 250);
}

function hTMLEncode(rawText) {
    if (rawText == null)
        return null;

    var htmlSafeText = "";
    for (var i = 0; i < rawText.length; i++) {
        var c = rawText.charAt(i);
        if (c == '<')
            htmlSafeText += "&lt;";
        else if (c == '>')
            htmlSafeText += "&gt;";
        else if (c == '"')
            htmlSafeText += "&quot;";
        else if (c == '&')
            htmlSafeText += "&amp;";
        else if (c == "\'")
            htmlSafeText += "&#39;";
        else
            htmlSafeText += c;
    }

    return htmlSafeText;
}

function disposeOfMoxieFlyoutWindow() {
	MoxieFlyout.hostPage.restore();
	var isFixed = MoxieFlyout.hasClass(document.body, "fixed");
	if (isFixed) {
		MoxieFlyout.removeClass(document.body, "fixed");
	}

	MoxieFlyout = MoxieFlyoutReset();
	MoxieFlyout.StorageSessionStorage = MySessionStorage();
	MoxieFlyout.StorageCookie = MyCustomCookieStorage();
	MoxieFlyout.StorageMixed = MyCustomStorage();
	MoxieFlyout.storage = MoxieFlyout.StorageMixed;
	MoxieFlyout.storage.read();
	detectDone = false;

	var flyoutHolderRef = document.getElementById("MoxieFlyoutHolder");
	if (flyoutHolderRef) {
		flyoutHolderRef.style.display='none';
	}


}