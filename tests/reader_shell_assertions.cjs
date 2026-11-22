// Dependency-free negative fixtures for the existing optional Playwright smoke.
const assert=require('node:assert/strict');
const {readerShellProblems}=require('../scripts/browser_assertions.cjs');
const good={scroll:390,headerCount:1,headerHeight:91,footerCount:1,footerTags:1,
 searchIcon:{width:18,height:18},themeIcons:2,visibleThemeIcons:1,
 chapterNavs:1,desktopChapterLinks:0,shareControls:1};
assert.deepEqual(readerShellProblems(good,390),[]);
assert.deepEqual(readerShellProblems({...good,scroll:500},390),['document horizontal overflow']);
assert(readerShellProblems({...good,headerHeight:1736},390).includes('shared header singleton/size'));
assert(readerShellProblems({...good,footerTags:2},390).includes('shared footer singleton'));
assert(readerShellProblems({...good,searchIcon:{width:1440,height:1440}},390).includes('search SVG computed size'));
assert(readerShellProblems({...good,visibleThemeIcons:2},390).includes('one visible appearance glyph'));
assert(readerShellProblems({...good,scroll:1440,headerHeight:67,chapterNavs:1,desktopChapterLinks:0},1440).includes('desktop chapter navigation hidden'));
assert.deepEqual(readerShellProblems({...good,scroll:1440,headerHeight:67,chapterNavs:1,desktopChapterLinks:9},1440),[]);
console.log('PASS: seven Reader 71 failure fixtures and responsive shell success');
