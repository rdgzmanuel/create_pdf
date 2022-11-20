from IPython.display import display, HTML
from xhtml2pdf import pisa

graphs = [
    "images\orders_category",
    "images\orders_subcategory",
    "images\orders_year",
    "images\profits_year"
]


def report_block_template(graph_url, caption=''):
    graph_block = (''
        '<a href="{graph_url}" target="_blank">'  # Open the interactive graph when you click on the image
            '<img style="height: 400px;" src="{graph_url}.png">'
        '</a>')

    report_block = ('' +
        graph_block +
        '{caption}' + # Optional caption to include below the graph
        '<br>'      + # Line break
        '<a href="{graph_url}" style="color: rgb(190,190,190); text-decoration: none; font-weight: 200;" target="_blank">'+
            'Click to comment and see the interactive graph' +  # Direct readers to Plotly for commenting, interactive graph
        '</a>' +
        '<br>' +
        '<hr>') # horizontal line

    return report_block.format(graph_url=graph_url, caption=caption)


def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    with open(output_filename, "w+b") as result_file:
        # convert HTML to PDF
        pisa_status = pisa.CreatePDF(
                source_html,                # the HTML to convert
                dest=result_file)           # file handle to recieve result

    # return True on success and False on errors
    return pisa_status.err


if __name__ == "__main__":
    static_report = ''

    for graph_url in graphs:
        _static_block = report_block_template(graph_url, caption='')

        static_report += _static_block
    convert_html_to_pdf(static_report, "report.pdf")
