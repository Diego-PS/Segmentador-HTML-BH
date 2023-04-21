const { JSDOM } = require('jsdom');
const fs = require('fs');
const { PageDO } = require('./PageDO');

class HtmlDO {
    html
    dom
    page_container
    pages_as_elements
    pages
    caixa_cinza_elements

    getCaixaCinzaClassWithSize = (pages, px_siz) => {

        let siz = pages.length
    
        let caixaCinzaClass = undefined
        for (let i = siz-1; i >= 0; i--) {
            
            let page = pages[i]
    
            let lastChild = page.lastChild
    
            if (lastChild.children.length == 2) {
                lastChild = page.children[page.children.length-2]
            }
    
            if (this.dom.window.getComputedStyle(lastChild).fontSize == `${px_siz}.000000px`) {
                caixaCinzaClass = this.dom.window.getComputedStyle(lastChild).fontFamily
                break
            }
        }
    
        return caixaCinzaClass
    }

    getCaixaCinzaClass = pages => {
        return {
            principal : this.getCaixaCinzaClassWithSize(pages, '48'),
            secundario : this.getCaixaCinzaClassWithSize(pages, '44')
        }
    }

    constructor(html_file_path) {
        this.html = fs.readFileSync(html_file_path, 'utf-8')
        this.dom = new JSDOM(this.html)
        this.page_container = this.dom.window.document.getElementById('page-container')
        this.pages_as_elements = Array.from(this.page_container.children).map(child => child.children[0])
        
        const caixa_cinza_class = this.getCaixaCinzaClass(this.pages_as_elements) 
        this.caixa_cinza_elements = {
            principal : Array.from(this.dom.window.document.getElementsByClassName(caixa_cinza_class.principal)),
            secundario : Array.from(this.dom.window.document.getElementsByClassName(caixa_cinza_class.secundario))
        }

        this.pages = []
        for (const page of this.pages_as_elements) {
            this.pages.push(new PageDO(page, this))
        }
    }
}

module.exports = { HtmlDO }