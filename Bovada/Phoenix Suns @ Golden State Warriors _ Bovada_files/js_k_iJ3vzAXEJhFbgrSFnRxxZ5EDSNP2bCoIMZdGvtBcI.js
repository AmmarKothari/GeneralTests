
/**
 * @file
 * Select the language from the URL and sets it as the value of the cookie LANGUAGE
 *  only in case this cookie doesn't exists.
 */
(function () {
    function getLanguageFromUrl() {
        var languages = Drupal.settings.websites.languages;
        var url = window.location.pathname;
        var urlFirstPath = null;

        if (url.split('/').length > 1) {
            urlFirstPath = url.split('/')[1].toLowerCase();
        }

        return languages.hasOwnProperty(urlFirstPath) ? languages[urlFirstPath].code : getDefaultLanguage();
    }


    function getDefaultLanguage() {
        var languages =  Drupal.settings.websites.languages;
        for (var code in languages) {
            if (languages.hasOwnProperty(code)) {
                var language = languages[code];
                if (language.default) {
                    return language.code;
                }
            }
        }
    }


    function setLanguage() {

        var language = UiAppCookies.getItem("LANGUAGE");
        if(!language) {
            UiAppCookies.setItem("LANGUAGE", getLanguageFromUrl());
        }

    }

    setLanguage();
})();;
;
