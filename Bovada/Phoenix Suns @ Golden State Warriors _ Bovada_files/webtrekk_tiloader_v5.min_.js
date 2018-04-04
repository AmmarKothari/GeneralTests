/** start TagIntegration loader  */
(function(d,c,a,f){d.wts=d.wts||[];var g=function(b){var a="";b.customDomain&&b.customPath?a=b.customDomain+"/"+b.customPath:b.tiDomain&&b.tiId&&(a=b.tiDomain+"/resp/api/get/"+b.tiId+"?url="+encodeURIComponent(d.location.href)+"&v=5");if(b.option)for(var c in b.option)a+="&"+c+"="+encodeURIComponent(b.option[c]);return a};if(-1===c.cookie.indexOf("wt_r=1")){var e=c.getElementsByTagName(a)[0];a=c.createElement(a);a.async=!0;a.onload=function(){if("undefined"!==typeof d.wt_r&&!isNaN(d.wt_r)){var b=
new Date,a=b.getTime()+1E3*parseInt(d.wt_r);b.setTime(a);c.cookie="wt_r=1;path=/;expires="+b.toUTCString()}};a.src="//"+g(f);e.parentNode.insertBefore(a,e)}})(window,document,"script",_tiConfig);

/** end TagIntegration loader */