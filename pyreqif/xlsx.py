#!/usr/bin/env python2
import io
import os.path
from lxml import etree
import pyreqif.extractOleData
#import openpyxl
#from openpyxl.drawing.image import Image
import xlsxwriter
from PIL import Image

def write_excel_line(worksheet, item, row, cols, depth, basepath, format):
    max_height = 0

    for col, value in item.items():
        files = []
        if col not in cols:
            continue
        if type(value) is not bytes:
            value = value.encode("utf8")
        if value is not None:
            if b"<" in value and b">" in value:
                try:
                    tree = etree.parse(io.BytesIO(value))
                    root = tree.getroot()
                    for element in root.iter("object"):
                        rtfFilename = os.path.join(basepath, element.attrib["data"])
                        if rtfFilename.endswith(".ole"):
                            files += pyreqif.extractOleData.extractOleData(rtfFilename)
                        else:
                            files += [rtfFilename]
                        if len(files) > 0 and files[0][-3:].lower() not in ["png","jpeg","jpg","bmp","wmf","emf"]:
                            for key in element.attrib:
                                del element.attrib[key]
                            element.tag = "a"
                            element.set("href", files[0])
                            element.text = "linked file: " + files[0]
                    value = "".join(root.itertext())
                    value = value.encode("utf8")
                except:
                    pass
#        worksheet.cell(row=row, column=cols.index(col)+1). value=value.decode("utf-8")
#        worksheet.row_dimensions[row].outlineLevel = depth
        worksheet.write(row, cols.index(col), value.decode("utf-8"))
        for file in files:
            if file[-3:].lower() in ["png", "jpeg", "jpg", "bmp", "wmf", "emf"]:
                im = Image.open(file)
                im.close()
                _, height = im.size
                max_height = max(height, max_height)
                worksheet.set_row(row, max_height, None, {'level': depth})

            if file[-3:].lower() in ["png", "jpeg", "jpg", "bmp", "wmf", "emf"]:
                worksheet.insert_image(row, cols.index(col), file)
    if max_height == 0:
        worksheet.set_row(row, None, format, {'level': depth})

def dump(myDoc, outfile, basepath = None):
    if basepath is None:
        basepath = os.path.dirname(outfile)
    #workbook = openpyxl.Workbook()
    #worksheet = workbook.active
    #workbook.title = "Export"
    workbook = xlsxwriter.Workbook(outfile)
    worksheet = workbook.add_worksheet("Export")

    cell_format = workbook.add_format()
    cell_format.set_text_wrap()

    cols = myDoc.fields
    colNr = 0
#    colNr = 1
    for col in cols:
        worksheet.write(0, colNr, col)
#        worksheet.cell(row=1, column=colNr).value = col
        colNr += 1
    cols = myDoc.fields

    row = 0
#    row = 1

    for child in myDoc.hierarchy:
        for item, depth in  myDoc.hierach_iterator(child, cols):
            row += 1
            write_excel_line(worksheet, item, row, cols, depth, basepath, cell_format)
#    workbook.save(filename=outfile)
    workbook.close()
