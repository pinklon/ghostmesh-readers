// Shared with the browser regression fixture. Catalog size is not a migration constant.
async function archiveComplete(page,catalog){
 return await page.locator('.gm-card').count()===catalog.readers.length;
}
// Browser-only computed shell witness for a newly drafted Reader. Structural
// checks cannot catch an oversized SVG or a CSS selector hiding the wrong icon.
async function currentReaderShell(page) {
 return page.evaluate(() => {
  const visible = el => !!el && getComputedStyle(el).visibility !== 'hidden'
      && getComputedStyle(el).display !== 'none' && el.getBoundingClientRect().width > 0
      && el.getBoundingClientRect().height > 0;
  const size = el => el ? {width:el.getBoundingClientRect().width,
                         height:el.getBoundingClientRect().height} : {width:0,height:0};
  const themeIcons = [...document.querySelectorAll('.gm-theme-control .gm-theme-sun, .gm-theme-control .gm-theme-moon')];
  const chapterNavs = [...document.querySelectorAll('nav[aria-label="Reader chapter navigation"], nav[aria-label="Article contents"]')];
  return {
   viewport:innerWidth,
   scroll:document.documentElement.scrollWidth,
   headerCount:document.querySelectorAll('header.gm-site-header').length,
   footerCount:document.querySelectorAll('footer.gm-reader-footer').length,
   footerTags:document.querySelectorAll('footer').length,
   headerHeight:size(document.querySelector('header.gm-site-header')).height,
   searchIcon:size(document.querySelector('.gm-search-control svg')),
   themeIcons:themeIcons.length,
   visibleThemeIcons:themeIcons.filter(visible).length,
   theme:document.documentElement.dataset.theme,
   chapterNavs:chapterNavs.length,
   desktopChapterLinks:chapterNavs.flatMap(nav=>[...nav.querySelectorAll('a')]).filter(visible).length,
   shareControls:document.querySelectorAll('[data-gm-share]').length
  };
 });
}
function readerShellProblems(m, width) {
 const out=[];
 if(m.scroll>width+1)out.push('document horizontal overflow');
 if(m.headerCount!==1 || m.headerHeight===0 || m.headerHeight>(width>=1000?140:170))out.push('shared header singleton/size');
 if(m.footerCount!==1 || m.footerTags!==1)out.push('shared footer singleton');
 if(m.searchIcon.width<10 || m.searchIcon.height<10 || m.searchIcon.width>40 || m.searchIcon.height>40)out.push('search SVG computed size');
 if(m.themeIcons!==2 || m.visibleThemeIcons!==1)out.push('one visible appearance glyph');
 if(width>=1000 && m.chapterNavs>0 && m.desktopChapterLinks===0)out.push('desktop chapter navigation hidden');
 if(m.shareControls!==1)out.push('shared share controls');
 return out;
}
module.exports={archiveComplete,currentReaderShell,readerShellProblems};
