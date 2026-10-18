// Shared with the browser regression fixture. Catalog size is not a migration constant.
async function archiveComplete(page,catalog){
 return await page.locator('.gm-card').count()===catalog.readers.length;
}
module.exports={archiveComplete};
