# -*- coding: utf-8 -*-


import pickle
from operator import itemgetter
import subprocess
import os
import shutil
from chempy import Substance


def latexify(chemical):
    try:
        c = Substance.from_formula(chemical)
        l = c.latex_name

        l = l.replace("_{", "$_{\\text{")
        l = l.replace("^{", "$^{\\text{")
        l = l.replace("}", "}}$")

    except:
        l = chemical

    return l

def latexify_list(chemical_string):
    chemicals_list = chemical_string.split("+")

    new_chemical_string = ""
    for chemical in chemicals_list:
        chemical = latexify(chemical)
        if new_chemical_string:
            new_chemical_string += "   +   " + chemical
        else:
            new_chemical_string += chemical

    return new_chemical_string




def create_tex(name, op):
    # name = sid
    global temp_tex, weighin_tex, header_tex, preamble_tex, end_tex

    idexdir = os.getcwd()
    idexdir = idexdir.replace("\\", "/")
    # print(idexdir)
    # return
    std_set = pickle.load(open("../IDEXDATA/DATA/std_settings.pkl","rb"))
    home = std_set["HOME"]

    experiment_dict = pickle.load(open(home + "/" + op + "/" + op + "_experiments.idx","rb"))

    total = experiment_dict[name]
    header = total["INFORMATION"]

    shortop = op.split("(")[1].split(")")[0]

    # Check all Variables for non-conform Latex-characters

    # LongInput
    idea = header["IDEA"]

    if idea:
        idea = idea.replace("\n", "\\\\ \n")
        idea = idea + "\\\\"
    else:
        idea = "\\vspace{0.8cm}"

    try:
        additives = total["SWI"]["ADDITIVES"]
    except:
        additives = ""
    if additives:
        additives = additives.replace("\n", "\\\\ \n")
        additives = additives + "\\\\ \\\\"
    else:
        additives = "\\vspace{1cm}"

    expdetails = total["TP"]["EXPERIMENTAL DETAILS"]
    if expdetails:
        expdetails = expdetails.replace("\n", "\\\\ \n")
        expdetails = expdetails + "\\\\"
    else:
        expdetails = "\\vspace{1.5cm}"
    analytics = total["ANALYTICS"]["ANALYTICAL DETAILS"]
    if analytics:
        analytics = analytics.replace("\n", "\\\\ \n")
        analytics = analytics + "\\\\"
    else:
        analytics = "\\vspace{2cm}"
    appearance = total["ANALYTICS"]["APPEARANCE"]
    if appearance:
        appearance = appearance.replace("\n", "\\\\ \n")
        appearance = appearance + "\\\\"
    else:
        appearance = "\\vspace{2cm}"
    conclusion = total["RESULT"]["CONCLUSION"]
    if conclusion:
        conclusion = conclusion.replace("\n", "\\\\ \n")
        conclusion = conclusion + "\\\\"
    else:
        conclusion = "\\vspace{2cm}"

    # Take care of products (\quad produces spaces in latex)
    product = ""
    for i in total["RESULT"]["PRODUCTS"]:
        print(i)
        if i["IDENTIFIER"]:
            product += i["IDENTIFIER"] + ": \\quad\\quad\\quad " +  latexify_list(i["PRODUCT"]) + "\\\\ \n"
        elif i["PRODUCT"]:
            product += latexify_list(i["PRODUCT"]) + "\\\\ \n"

    for i in ["%", "&", "#", "$"]:
        substr = i
        insertbackslash = "\\"
        idea = (insertbackslash + substr).join(idea.split(substr))
        additives = (insertbackslash + substr).join(additives.split(substr))
        expdetails = (insertbackslash + substr).join(expdetails.split(substr))
        analytics = (insertbackslash + substr).join(analytics.split(substr))
        appearance = (insertbackslash + substr).join(appearance.split(substr))
        conclusion = (insertbackslash + substr).join(conclusion.split(substr))
        if i != "$":
            product = (insertbackslash + substr).join(product.split(substr))



    weighin_tex = ""
    temp_tex = ""

    # =============================================================================
    #   """ Header """
    # =============================================================================

    preamble_tex = f"""
        % !TeX program = pdflatex
        \\documentclass[11pt,a4paper]{{article}}
        \\usepackage[utf8]{{inputenc}}
        \\usepackage[sfdefault,lining]{{FiraSans}}
        \\usepackage{{amsmath}}
        \\usepackage{{amssymb}}
        \\usepackage[left=20mm,right=20mm,top=10mm,bottom=2cm]{{geometry}}
        \\usepackage{{tabularx}}
        \\usepackage{{tikz}}
        \\usepackage{{graphicx}}
        \\usetikzlibrary{{calc}}
        \\usepackage[version=4]{{mhchem}}
        \\usepackage{{colortbl}}
        \\usepackage{{gensymb}}
        \\usepackage{{setspace}}

        \\usepackage{{tcolorbox}}
        \\tcbuselibrary{{skins,breakable}}

        \\setlength\\parindent{{0pt}}
        \\arrayrulecolor{{black}}
        \\setlength{{\\arrayrulewidth}}{{1pt}}
        \\pagestyle{{empty}}
        \\renewcommand*{{\\arraystretch}}{{1.8}}%... and increase the row height

        \\newcolumntype{{A}}{{>{{\\hsize=1.2\\hsize\\linewidth=\\hsize\\centering\\arraybackslash}}X}}
        \\newcolumntype{{B}}{{>{{\\hsize=.8\\hsize\\linewidth=\\hsize\\centering\\arraybackslash}}X}}
        \\newcolumntype{{C}}{{>{{\\centering\\arraybackslash}}X}}
        \\newcolumntype{{D}}{{>{{\\hsize=.4\\hsize\\linewidth=\\hsize\\centering\\arraybackslash}}X}}
        \\newcolumntype{{E}}{{>{{\\hsize=1.15\\hsize\\linewidth=\\hsize\\centering\\arraybackslash}}X}}
        \\newcolumntype{{G}}{{>{{\\hsize=1.69\\hsize\\linewidth=\\hsize\\centering\\arraybackslash}}X}}
        \\newcolumntype{{H}}{{>{{\\hsize=.77\\hsize\\linewidth=\\hsize}}X}}
        \\newcolumntype{{I}}{{>{{\\hsize=1.4\\hsize\\linewidth=\\hsize\\centering\\arraybackslash}}X}}
        \\newcolumntype{{J}}{{>{{\\hsize=.2\\hsize\\linewidth=\\hsize\\centering\\arraybackslash}}X}}
        \\begin{{document}}
    """

    trgt = latexify(header["TARGET"])
    if not header["TAG"] or not trgt:
        tagtrgtseparator = ""
    else:
        tagtrgtseparator = "\\quad $|$ \\quad"

    header_tex = f"""
        \\begin{{tcolorbox}}[
        	width = 0.8\\linewidth,
        	colback = white,
        	boxrule = 1pt,
        	colframe = white,
        	box align = top,
        	nobeforeafter,
        	]
        	\\textbf{{{{\\Huge {header["SAMPLE ID"]}}}}}\\\\
        	\\\\
        	{{\\Large {header["TAG"]} {tagtrgtseparator} {trgt}}}
        \\end{{tcolorbox}}
        \\begin{{tcolorbox}}[
        	width = 0.2\\linewidth,
        	colback = white,
        	boxrule = 1pt,
        	colframe = white,
        	box align = top,
        	nobeforeafter
        	]

        	\\raggedleft	{header["DATE"]}

        \\end{{tcolorbox}}
        \\hrule height 2pt

        \\vspace{{0.6cm}}

        \\tcbset{{enhanced jigsaw,
        	breakable,
        	attach boxed title to top left,
        	fonttitle = \\bfseries\\large,
        	coltitle = black,
        	boxed title style = {{colback=white, colframe = white}},
        	colback = white,
        	boxrule = 1pt,
        	colframe = black}}

        % IDEA
        \\begin{{tcolorbox}}[
        	title = {{\\smash{{\\raisebox{{-0mm}}{{\\includegraphics[width=5mm,height=5mm]{{{idexdir + "/data/md/"}idea.png}}}}}} \\hspace{{0.5mm}} \\large Idea}},
        	colframe = white
        	]
        	{idea}
        \\end{{tcolorbox}}

        \\vspace{{0.2cm}}
        """

    reactants  = total["REACTION"]["REACTANTSBAL"]
    reactants = reactants.replace("[sub][size=11.2sp]", "$_{\\text{")
    reactants = reactants.replace("[sup][size=11.2sp]", "$^{\\text{")
    reactants = reactants.replace("[/size][/sub]", "}}$")
    reactants = reactants.replace("[/size][/sup]", "}}$")

    products  = total["REACTION"]["PRODUCTSBAL"]
    products = products.replace("[sub][size=11.2sp]", "$_{\\text{")
    products = products.replace("[sup][size=11.2sp]", "$^{\\text{")
    products = products.replace("[/size][/sub]", "}}$")
    products = products.replace("[/size][/sup]", "}}$")

    reaction_tex = f"""
        % Reaction
        \\begin{{tcolorbox}}[
        	title = {{\\smash{{\\raisebox{{-1mm}}{{\\includegraphics[width=5mm,height=5mm]{{{idexdir + "/data/md/"}react.png}}}}}} \\hspace{{0.5mm}} \\large Reaction}},
        	colframe = white,
        	top = 1mm,
        	bottom = 1mm
        	]
        	\\renewcommand\\tabularxcolumn[1]{{m{{#1}}}}
        	\\begin{{tabularx}}{{\\textwidth}}{{IJI}}
        		\\raggedleft\\arraybackslash {reactants} & $\\longrightarrow$ & \\raggedright\\arraybackslash {products}\\\\
        	\\end{{tabularx}}
        \\end{{tcolorbox}}
        \\vspace{{0.2cm}}
        """

    # =============================================================================
    #   """ WeighIn """
    # =============================================================================

    weighin = total["SWI"]["REACTANTS"]

    table = ""
    for i in weighin:
        reac = latexify(i["REACTANT"])
        eq = str(i["EQUIVALENT"])
        M = str(i["MOLAR MASS"])
        mol = str(i["MOL"])
        mass = str(i["MASS"])

        row = reac + " & " + eq + " & " + M + " & " + mol + " & " + mass

        if i == weighin[-1]:
            row += "\\\\ \n"
        else:
            row += "\\\\ \\hline \n"

        table += row

    weighin_tex = f"""
        % Sample weigh-in
        \\begin{{tcolorbox}}[
        	title = {{\\smash{{\\raisebox{{-1mm}}{{\\includegraphics[width=5mm,height=5mm]{{{idexdir + "/data/md/"}bal.png}}}}}} \\hspace{{0.5mm}} \\large Sample Weigh-In}},
        	colframe = white,top = 0mm,
        	bottom = 0mm
        	]
        \\begin{{tabularx}}{{\\textwidth}}{{ABCCC}}
        	& & & \\textbf{{Net weight:}} & 100\\,mg \\\\
        \\end{{tabularx}}

        \\begin{{tcolorbox}}[boxsep = 0mm,
        	left = 0mm,
        	right = 0mm,
        	top = 0mm,
        	bottom = 0mm,
        	enhanced,
        	attach boxed title to top left,
        	fonttitle = \\bfseries\\large,
        	coltitle = black,
        	boxed title style = {{colback=white, colframe = white}},
        	colback = white,
        	boxrule = 1pt,
        	colframe = black
        	]

        	\\begin{{tabularx}}{{\\textwidth}}{{A|B|C|C|C}}
        		\\textbf{{Reactants}} & \\textbf{{EQ}} & \\textbf{{M / g$\\cdot$mol$^{{-1}}$}} & \\textbf{{n / mmol}} & \\textbf{{m / mg}} \\\\ \\hline
        		{table}
        	\\end{{tabularx}}
        \\end{{tcolorbox}}

        % Additives
        \\begin{{tcolorbox}}[title = Additives,
        	enhanced,
        	attach boxed title to top left,
        	fonttitle = \\bfseries,
        	coltitle = black,
        	boxed title style = {{colback=white, colframe = white}},
        	colback = white,
        	boxrule = 1pt,
        	colframe = black
        	]
        	{additives}
        \\end{{tcolorbox}}
        \\end{{tcolorbox}}

        \\vspace{{0.8cm}}
        """

    # =============================================================================
    #   """ Temp """
    # =============================================================================

    method = total["TP"]["METHOD"]
    units = total["TP"]["UNITS"]
    temp = total["TP"]["PROGRAM"]
    temp_tex_table = ""
    temp_tex_elements = ""

    meth = ""
    tp = ""

    for n,i in enumerate(method):
        if i == "Oil Pressure":
            title = "Oil P."
        elif i == "Heating Capacity":
            title = "Heat. Cap."
        else:
            title = i

        val = method[i]
        if "Furnace" in val:
            val = val.replace("Furnace", "Furn.")



        if (n+1) % 3 == 0:
            meth += "\\textbf{{" + title.upper() + ":}} & " + val + " \\\\ \n"
        else:
            meth += "\\textbf{{" + title.upper() + ":}} & " + val + " &"

    # methods have a different number of values
    k = len(method) % 3
    if k == 1:
        meth += "& & & \\\\ \n"
    elif k == 2:
        meth += " & \\\\ \n"

    for i,j in enumerate(temp):
        for k,l in enumerate(j):
            if k%4==0 and k!=0:
                tp += j[l] + " \\\\ \n"
            else:
                tp += j[l] + " & "

    # take care of %
    try:
        substr = "%"
        insertbackslash = "\\"
        meth = (insertbackslash + substr).join(meth.split(substr))
    except:
        pass

    if units["TSTART"] == "°C":
        tstart = "$^{\circ}$C"
    else:
        tstart = "K"

    if units["RAMP"] == "°C·min[sup][size=10sp]-1[/size][/sup]":
        ramp = "$^{\circ}$C$\cdot$min$^{-1}$"
    elif units["RAMP"] == "°C·h[sup][size=10sp]-1[/size][/sup]":
        ramp = "$^{\circ}$C$\cdot$h$^{-1}$"
    else:
        ramp = units["RAMP"]

    if units["TEND"] == "°C":
        tend = "$^{\circ}$C"
    else:
        tend = "K"


    temp_tex = f"""
        % Temperature Program
        \\begin{{tcolorbox}}[
        	title = {{\\smash{{\\raisebox{{-1mm}}{{\\includegraphics[width=5mm,height=5mm]{{{idexdir + "/data/md/"}stove.png}}}}}} \\hspace{{0.5mm}} \\large Temperature Program}},
        	colframe = white,
        	top = 0mm,
        	bottom = 0mm,
        	]

        \\begin{{tabularx}}{{\\textwidth}}{{XXXXXX}}
        {meth}
        \\end{{tabularx}}


        % Program
        \\begin{{tcolorbox}}[boxsep = 0mm, left = 0mm, right = 0mm, top = 0mm, bottom = 0mm,
        	enhanced,
        	attach boxed title to top left,
        	fonttitle = \\bfseries,
        	coltitle = black,
        	boxed title style = {{colback=white, colframe = white}},
        	colback = white,
        	boxrule = 1pt,
        	colframe = black]

        	\\begin{{tabularx}}{{\\textwidth}}{{D|EEEE}}
            \\textbf{{SEG.}} & \\textbf{{T$_{{\\text{{START}}}}$ / {tstart} }} & \\textbf{{RAMP / {ramp} }} & \\textbf{{T$_{{\\text{{END}}}}$ / {tend} }} & \\textbf{{DWELL / {units["DWELL"]}}} \\\\ \\cline{{1-5}}
            {tp}
            \\end{{tabularx}}
        \\end{{tcolorbox}}

        % Experimental Details
        \\begin{{tcolorbox}}[title = Experimental Details,
        	enhanced,
        	attach boxed title to top left,
        	fonttitle = \\bfseries,
        	coltitle = black,
        	boxed title style = {{colback=white, colframe = white}},
        	colback = white,
        	boxrule = 1pt,
        	colframe = black]
        	{expdetails}
        \\end{{tcolorbox}}
        \\end{{tcolorbox}}

        \\vspace{{0.5cm}}

        """


    # =============================================================================
    #   """ End """
    # =============================================================================

    anamet = ""
    ana = total["ANALYTICS"]
    for n, i in enumerate(ana["METHODS"]):
        if i == "FLUORESCENCE":
            t = "FLUOR."
        else:
            t = i

        if ana["METHODS"][i]:
            if anamet and not anamet.endswith("\\\\ \n"):
                anamet += " & " + "$\\boxtimes$  " + t
                # anamet += "\\mbox{{\\quad\\quad $\\boxtimes$  " + t + "}}"
            else:
                anamet += "$\\boxtimes$  " + t

        else:
            if anamet and not anamet.endswith("\\\\ \n"):
                anamet += " & " + "$\\square$  " + t
            else:
                anamet += "$\\square$  " + t

        if (n+1) % 5 == 0 and n:
            anamet += "\\\\ \n"

    k = len(ana["METHODS"]) % 5

    anamet += (5-k) * "& "
    # if k == 1:
    #     anamet += " & & & &"
    # elif k == 2:
    #     anamet += " & & &"

    analytics_tex = f"""
        % Analytics
        \\begin{{tcolorbox}}[
        	title = {{\\smash{{\\raisebox{{-0.5mm}}{{\\includegraphics[width=5mm,height=5mm]{{{idexdir + "/data/md/"}ana.png}}}}}} \\hspace{{0.5mm}} \\large Analytics}},
        	colframe = white,
        	top = 0mm,
        	bottom = 0mm,
        	]

        	% Appearance
        	\\begin{{tcolorbox}}[title = Appearance,
        		enhanced,
        		attach boxed title to top left,
        		fonttitle = \\bfseries,
        		coltitle = black,
        		boxed title style = {{colback=white, colframe = white}},
        		colback = white,
        		boxrule = 1pt,
        		colframe = black]
        		{appearance}
        	\\end{{tcolorbox}}

        	\\vspace{{0.3cm}}


        	% Methods
        	\\begin{{tcolorbox}}[title = Methods,
        		enhanced,
        		attach boxed title to top left,
        		fonttitle = \\bfseries,
        		coltitle = black,
        		boxed title style = {{colback=white, colframe = white}},
        		colback = white,
        		boxrule = 1pt,
        		colframe = white]

            \\begin{{tabularx}}{{\\textwidth}}{{XXXXX}}
                {anamet} \\\\
            \\end{{tabularx}}
        	\\end{{tcolorbox}}

        	\\begin{{tcolorbox}}[title = Analytical Details,
        		enhanced,
        		attach boxed title to top left,
        		fonttitle = \\bfseries,
        		coltitle = black,
        		boxed title style = {{colback=white, colframe = white}},
        		colback = white,
        		boxrule = 1pt,
        		colframe = black]
        		{analytics}
        	\\end{{tcolorbox}}

        \\end{{tcolorbox}}

        \\vspace{{0.5cm}}

        """

    end_tex = f"""
        % Results
        \\begin{{tcolorbox}}[
        	title = {{\\smash{{\\raisebox{{-1mm}}{{\\includegraphics[width=5mm,height=5mm]{{{idexdir + "/data/md/"}res.png}}}}}} \\hspace{{0.5mm}} \\large Results}},
        	colframe = white,
        	top = 0mm,
        	bottom = 0mm,
        	]

        	% Products
        	\\begin{{tcolorbox}}[title = Products,
        		enhanced,
        		attach boxed title to top left,
        		fonttitle = \\bfseries,
        		coltitle = black,
        		boxed title style = {{colback=white, colframe = white}},
        		colback = white,
        		boxrule = 1pt,
        		colframe = white]
        		{product}
        	\\end{{tcolorbox}}

        	\\vspace{{0.3cm}}

        	% Conclusion
        	\\begin{{tcolorbox}}[title = Conclusion,
        		enhanced,
        		attach boxed title to top left,
        		fonttitle = \\bfseries,
        		coltitle = black,
        		boxed title style = {{colback=white, colframe = white}},
        		colback = white,
        		boxrule = 1pt,
        		colframe = black]
        		{conclusion}
        	\\end{{tcolorbox}}
        \\end{{tcolorbox}}
        \\end{{document}}

        """

    with open(home + "/" + op + "/tex/" + name + ".tex", "w", encoding='UTF-8') as f:
        f.write(preamble_tex)
        f.write(header_tex)
        f.write(reaction_tex)
        f.write(weighin_tex)
        f.write(temp_tex)
        f.write(analytics_tex)
        f.write(end_tex)

def create_pdf(name, op):
    std_set = pickle.load(open("../IDEXDATA/DATA/std_settings.pkl","rb"))
    home = std_set["HOME"]
    subprocess.call(['pdflatex', name + '.tex'], cwd = home + "/" + op + "/tex")

    if not os.path.exists(home + "/" + op + "/pdf"):
        os.makedirs(home + "/" + op + "/pdf")

    os.replace(home + "/" + op + "/tex/" + name + ".pdf", home + "/" + op + "/pdf/" + name + ".pdf")
    # subprocess.Popen(name + ".pdf", cwd= home + "/" + op + "/pdf", shell=True)

    os.remove(home + "/" + op + "/tex/" + name + ".aux")
    os.remove(home + "/" + op + "/tex/" + name + ".log")



def main():
    # create_tex()
    latexify_list("Al2O3 + UF6 + LaCl3 + Mar[w61]in")

if __name__ == "__main__":
    main()
