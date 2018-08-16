# -*- coding:utf-8 -*-


class Script(object):
    scrollToBottom = """var app = document.querySelector('div#app');window.scrollTo(app.width, app.offsetHeight);"""
    tryNewPage = """$('.trynew-btn a')[0].click();"""
    articleSTB = """var container = document.querySelector('div.page-container');window.scrollTo(container.width, container.offsetHeight);"""
    replyPaginate = """$('div.list-item.reply-wrap').eq({}).find('div div.paging-box a').eq(-1).trigger("click")"""
    commentPaninate = """var e = $.Event("keydown"); e.keyCode = 13;$('div.page-jump input').val({}).trigger(e);"""

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)