(function($){'use strict';$(document).ready(function(){$('.show-notification').click(function(e){var button=$(this);var style=$('.btn-notification-style.active').text();var message=$('.notification-message').val();var type=$('select.notification-type').val();var position=$('.tab-pane.active .position.active').attr('data-placement');if(style=='Bar'){$('.page-content-wrapper').pgNotification({style:'bar',message:message,position:position,timeout:0,type:type}).show();}else if(style=='Flip Bar'){$('.page-content-wrapper').pgNotification({style:'flip',message:message,position:position,timeout:0,type:type}).show();}else if(style=='Circle'){$('.page-content-wrapper').pgNotification({style:'circle',title:'John Doe',message:message,position:position,timeout:0,type:type,thumbnail:'<img width="40" height="40" style="display: inline-block;" src="assets/img/profiles/avatar2x.jpg" data-src="assets/img/profiles/avatar.jpg" data-src-retina="assets/img/profiles/avatar2x.jpg" alt="">'}).show();}else if(style=='Simple Alert'){$('.page-content-wrapper').pgNotification({style:'simple',message:message,position:position,timeout:0,type:type}).show();}else{return;}
e.preventDefault();});$('.position').click(function(){$(this).closest('.notification-positions').find('.position').removeClass('active');$(this).addClass('active');});$('.btn-notification-style').click(function(){var target=$(this).attr('data-type');$('a[href=#'+ target+']').tab('show');});$('a[data-toggle="tab"]').on('show.bs.tab',function(e){var position=$(this).data('type');$('a[href="'+position+'"]').tab('show')
$('.pgn').remove();});});})(window.jQuery);