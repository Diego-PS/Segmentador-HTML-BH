class PageDO {
    html
    page_div
    caixa_cinza_elements_of_page
    ordered_elements

    constructor(page, htmlDO) {
        this.html = htmlDO
        this.page_div = page
        const not_ordered = this.html.caixa_cinza_elements.principal.filter(element => Array.from(this.page_div.children).includes(element))
        const ordered = not_ordered.sort((a, b) => this.html.dom.window.getComputedStyle(a).bottom > this.html.dom.window.getComputedStyle(b).bottom)
        this.caixa_cinza_elements_of_page = ordered
        this.ordered_elements = []
        this.insert_caixa_cinza_texts()
    }

    insert_caixa_cinza_texts = () => {

        const added_caixas_cinzas = new Set()

        for (const element of Array.from(this.page_div.children)) {
            
            if (this.caixa_cinza_elements_of_page.includes(element) || !element.textContent || Array.from(element.children).filter(e => e.tagName == 'DIV').length != 0) continue

            for (const caixa_cinza of this.caixa_cinza_elements_of_page) {

                if (!added_caixas_cinzas.has(caixa_cinza)) {

                    const bottom_caixa_cinza_string = this.html.dom.window.getComputedStyle(caixa_cinza).bottom
                    const bottom_caixa_cinza = parseFloat(bottom_caixa_cinza_string.substring(0, bottom_caixa_cinza_string.length - 3))
                    const left_caixa_cinza_string = this.html.dom.window.getComputedStyle(caixa_cinza).left
                    const left_caixa_cinza = parseFloat(left_caixa_cinza_string.substring(0, left_caixa_cinza_string.length - 3))
                    
                    const bottom_element_string = this.html.dom.window.getComputedStyle(element).bottom
                    const bottom_element = parseFloat(bottom_element_string.substring(0, bottom_element_string.length - 3))
                    const left_element_string = this.html.dom.window.getComputedStyle(element).left
                    const left_element = parseFloat(left_element_string.substring(0, left_element_string.length - 3))
                    
                    if (bottom_caixa_cinza > bottom_element && Math.abs(left_caixa_cinza - left_element) < 100) {
                        this.ordered_elements.push(caixa_cinza)
                        added_caixas_cinzas.add(caixa_cinza)
                    }
                }
            }

            this.ordered_elements.push(element)
        }
    }
}

module.exports = { PageDO }