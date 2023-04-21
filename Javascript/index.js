const path = require("path")
const { HtmlDO } = require("./HtmlDO")
const fs = require("fs")

const html_file_directory = process.argv[2]
const html_file_name = html_file_directory.split('/').at(-1)
const file_name = html_file_name.substring(0, html_file_name.length - 5)

try {
    const html = new HtmlDO(html_file_directory)

    var section_title = ''
    var section_text = []

    const sections = []

    html.pages.map(page => page.ordered_elements).forEach(page => {
        page.forEach(element => {
            if (html.caixa_cinza_elements.todos.includes(element)) {
                if (section_title && section_text.length > 0) {
                    sections.push({ title: section_title, text: section_text })
                    section_text = []
                    section_title = ''
                }
                section_title += element.textContent
            } else {
                section_text.push(element.textContent)
            }
        })
    })

    if (section_text.length > 0) {
        if (!section_title) section_title = "PREFEITURA DE BELO HORIZONTE"
        sections.push({ title: section_title, text: section_text })
    }


    fs.writeFile(path.resolve(__dirname, '..', 'data', 'json_files', `${file_name}.json`), JSON.stringify(sections), (err, result) => {
        if (err) console.log(err)
    })
} catch (err) {
    console.log(err)
    fs.writeFile(path.resolve(__dirname, '..', 'data', 'json_files', `${file_name}.json`), JSON.stringify([]), (err, result) => {
        if (err) console.log(err)
    })
}