import sys
sys.path.append('../')
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import uproot
import helpers as hp
import mplhep
import math
import ROOT
ROOT.gROOT.SetBatch()



##COMPUTE PRESELECTION-EFFICIENCY
df_rec = uproot.open("../Tables/SignalTable_17d_mtexp.root")["SignalTable"].pandas.df()
df_sim = uproot.open("../Tables/SignalTable_17d_mtexp.root")["GenTable"].pandas.df()

presel_eff = len(df_rec)/len(df_sim.query("abs(rapidity)<0.5"))
print("-------------------------------------")
print("Pre-selection efficiency: ", presel_eff)

## FIT INVARIANT MASS SPECTRA
df = pd.read_parquet("../Utils/ReducedDataFrames/selected_df_data.parquet.gzip")
df_mc = pd.read_parquet("../Utils/ReducedDataFrames/selected_df_mc.parquet.gzip")
score_cuts_array = np.load("../Utils/Efficiencies/score_eff_syst_arr.npy")
bdt_eff_array = np.load("../Utils/Efficiencies/bdt_eff_syst_arr.npy")
selected_bdt_eff = 0.72
n_events040 = np.sum(uproot.open('../Utils/AnalysisResults_pPb.root')['AliAnalysisTaskHyperTriton2He3piML_default_summary;1'][11].values[:40-1])
branching_ratio = 0.25

signal_list040 = []
error_list040 = []
n1_list040 = []


ff = ROOT.TFile("../Results/inv_mass_fits.root", "recreate")
bkg_dir = ff.mkdir('bkg_pdf')
ff.cd()


for eff,cut in zip(bdt_eff_array, score_cuts_array):
    cut_string = f"model_output>{cut}"
    data040 = np.array(df.query(cut_string + " and 2.96<m<3.04 and centrality<=40 and abs(fZ) < 10")["m"])
    res040 = hp.unbinned_mass_fit(data040, eff, 'pol1', ff, bkg_dir, [0,40], [0,10], [0,35], split="", cent_string='040', bins = 34)

    mc_data = np.array(df_mc.query(cut_string + " and 2.96<m<3.04")["m"])
    mean_mass = np.mean(mc_data)
    hist = ROOT.TH1D(f'histo_mc_{eff}', f'histo_mc_{eff}', 500, 2.96, 3.04)
    for mc_entry in mc_data:
        hist.Fill(mc_entry - mean_mass + res040[4])
    
    ws_name = '' if eff != selected_bdt_eff else 'Workspace' 
    res_template = hp.unbinned_mass_fit_mc(data040, eff, 'pol1', hist, ff, bkg_dir, [0,40], [0,10], [0,35], split="", cent_string='040', bins = 34, sign_range = [res040[-2], res040[-1]])

    signal_list040.append(res_template[0])
    error_list040.append(res_template[1])
    n1_list040.append(res_template[2])


signal_array040 = np.array(signal_list040)
error_array040 = np.array(error_list040)




###COMPUTE YIELD############################


corrected_counts = signal_array040/n_events040/branching_ratio/presel_eff/bdt_eff_array
corrected_error = error_array040/n_events040/branching_ratio/presel_eff/bdt_eff_array
Yield = np.float64(corrected_counts[bdt_eff_array==selected_bdt_eff]  / 2)
Yield = Yield/0.98   #absorption correction

stat_error = np.float64(corrected_error[bdt_eff_array==selected_bdt_eff] / 2)
# syst_error = float(np.std(corrected_counts) / corrected_counts[bdt_eff_array==selected_bdt_eff])
syst_error = 0.14*Yield
pt_shape_syst = 0.07*Yield
abs_syst = 0.041*Yield
syst_error = np.sqrt(syst_error**2 + pt_shape_syst**2 + abs_syst**2)
print("-------------------------------------")
print(f"Yield [(matter + antimatter) / 2] 0-40% = {Yield:.3e} +- {stat_error:.3e} (stat.) +- {syst_error:.3e} (syst.)")
#############################################

###COMPUTE S3
protonVals = [{"bin":[0.0, 5.0], "measure": [2.280446e+00, 4.394273e-03, 1.585968e-01, 7.001060e-02]},
{"bin":[5.0, 10.0], "measure": [1.853576e+00, 3.901768e-03, 1.284426e-01, 5.548104e-02]},
{"bin":[10.0, 20.0], "measure": [1.577375e+00, 2.739986e-03, 1.084793e-01, 4.467687e-02]},
{"bin":[20.0, 40.0], "measure": [1.221875e+00, 1.735134e-03, 8.190972e-02, 3.347605e-02]},
{"bin":[40.0, 60.0], "measure": [8.621290e-01, 1.381181e-03, 5.608663e-02, 2.265973e-02]},
{"bin":[60.0, 80.0], "measure": [5.341445e-01, 1.034190e-03, 3.408551e-02, 1.377331e-02]},
{"bin":[80.0, 100.0], "measure": [2.307767e-01, 6.969543e-04, 1.450569e-02, 6.911692e-03]}]


lambdaVals = [{"bin": [0.0, 5.0], "measure": [1.630610e+00, 7.069538e-03, 1.448270e-01, 7.144051e-02]},
{"bin": [5.0, 10.0], "measure": [1.303508e+00, 6.313141e-03, 1.122199e-01, 5.217514e-02]},
{"bin": [10.0, 20.0], "measure": [1.093400e+00, 4.432728e-03, 9.410049e-02, 4.447422e-02]},
{"bin": [20.0, 40.0], "measure": [8.332270e-01, 3.036428e-03, 6.919569e-02, 3.205334e-02]},
{"bin": [40.0, 60.0], "measure": [5.678968e-01, 2.357040e-03, 4.722551e-02, 2.110751e-02]},
{"bin": [60.0, 80.0], "measure": [3.355044e-01, 1.855427e-03, 2.871323e-02, 1.389226e-02]},
{"bin": [80.0, 100.0], "measure": [1.335216e-01, 1.353847e-03, 1.142858e-02, 6.444149e-03]}]



lambdaAv040 = hp.computeAverage(lambdaVals,40)


# d$N$/d$\eta$ obtained by simple weighted average of the values published in https://arxiv.org/pdf/1910.14401.pdf
x_pPb040=np.array([29.4], dtype=np.float64)
xe_pPb040=np.array([0.6], dtype=np.float64)


hp_ratio_040 = np.array([2*Yield / lambdaAv040[0]], dtype=np.float64)
hp_ratiostat040 = np.array([hp_ratio_040[0] * hp.myHypot(stat_error / Yield, lambdaAv040[1] / lambdaAv040[0])], dtype=np.float64)
hp_ratiosyst040 = np.array([hp_ratio_040[0] * hp.myHypot(syst_error / Yield, lambdaAv040[2] / lambdaAv040[0])], dtype=np.float64)

print("-------------------------------------")
print(f"Hyp/Lambda 0-40% = {hp_ratio_040[0]:.2e} +- {hp_ratiostat040[0]:.2e} (stat.) +- {hp_ratiosyst040[0]:.2e} (syst.)")

kBlueC  = ROOT.TColor.GetColor("#2077b4");
kRedC  = ROOT.TColor.GetColor("#d62827");
kGreenC  = ROOT.TColor.GetColor("#2ba02b");
kOrangeC  = ROOT.TColor.GetColor("#ff7f0f");
kVioletC  = ROOT.TColor.GetColor("#9467bd");
kPinkC  = ROOT.TColor.GetColor("#e377c1");
kGreyC  = ROOT.TColor.GetColor("#7f7f7f");
kBrownC  = ROOT.TColor.GetColor("#8c564c");
kAzureC  = ROOT.TColor.GetColor("#18becf");
kGreenBC  = ROOT.TColor.GetColor("#bcbd21");

hp_ratio_csm_3 = ROOT.TGraphErrors("../Utils/ProdModels/hyp_p_ratio_155_3.dat","%lg %*s %*s %*s %*s %*s %lg %*s")
hp_ratio_csm_1 = ROOT.TGraphErrors("../Utils/ProdModels/hyp_p_ratio_155_1.dat","%lg %*s %*s %*s %*s %*s %lg %*s")

fin = ROOT.TFile('../Utils/ProdModels/vanilla_CSM_predictions_H3L_to_P.root')
hp_ratio_csm_van = fin.Get('gCSM_3HL_over_p')


hp_ratio_csm_1.SetLineColor(16)
hp_ratio_csm_1.SetLineWidth(2)
hp_ratio_csm_1.SetTitle("CSM with T=155MeV, Vc = dV/dy")


hp_ratio_csm_3.SetLineColor(16)
hp_ratio_csm_3.SetLineWidth(2)
hp_ratio_csm_3.SetLineStyle(2)
hp_ratio_csm_3.SetTitle("CSM with T=155MeV, Vc = 3dV/dy")

n = hp_ratio_csm_1.GetN()
grshade = ROOT.TGraph(2*n)
for i in range(n) : 
   grshade.SetPoint(i, hp_ratio_csm_3.GetPointX(i), hp_ratio_csm_3.GetPointY(i))
   grshade.SetPoint(n + i, hp_ratio_csm_1.GetPointX(n - i -1), hp_ratio_csm_1.GetPointY(n - i - 1))
   
grshade.SetFillColorAlpha(16, 0.571)
# grshade.SetFillStyle(3013)


hp_ratio_csm_van.SetLineColor(kOrangeC)
hp_ratio_csm_van.SetLineWidth(2)
hp_ratio_csm_van.SetTitle("Full canonical SHM")


hp_2body = ROOT.TGraphErrors("../Utils/ProdModels/hp_ratio_2body_coal.csv","%lg %lg %lg")
hp_2body.SetLineColor(kBlueC)
hp_2body.SetMarkerColor(kBlueC)
hp_2body.SetTitle("2-body coalescence")
hp_3body = ROOT.TGraphErrors("../Utils/ProdModels/hp_ratio_3body_coal.csv","%lg %lg %lg")
hp_3body.SetLineColor(kAzureC)
hp_3body.SetMarkerColor(kAzureC)
hp_3body.SetTitle("3-body coalescence")

# for i in range(hp_2body.GetN()):
#     hp_2body.GetY()[i] /= 1.5
#     hp_2body.GetEY()[i] /= 1.5

# for i in range(hp_3body.GetN()):
#     hp_3body.GetY()[i] /= 1.5
#     hp_3body.GetEY()[i] /= 1.5

hp_3body.SetFillColorAlpha(kAzureC, 0.571)
hp_2body.SetFillColorAlpha(kBlueC, 0.571)

mg = ROOT.TMultiGraph()
mg.Add(hp_2body)
mg.Add(hp_3body)
# mg.SetMinimum(1e-7)
# mg.SetMaximum(6e-6)


cv = ROOT.TCanvas("cv")
cv.SetBottomMargin(0.14)
frame=cv.DrawFrame(5., 1e-7, 200, 6e-6,";#LTd#it{N}_{ch}/d#it{#eta}#GT_{|#it{#eta}|<0.5}; {}_{#Lambda}^{3}H/p")
frame.GetXaxis().SetTitleOffset(1.25)
cv.SetLogx()
cv.SetLogy()
mg.Draw("4al same")
grshade.Draw("f same")
hp_ratio_csm_1.Draw("L same")
hp_ratio_csm_3.Draw("L same")
# hp_ratio_csm_van.Draw("L same")
mg.GetYaxis().SetRangeUser(1e-8, 1e-5)
mg.GetXaxis().SetTitle('#LTd#it{N}_{ch}/d#it{#eta}#GT_{|#it{#eta}|<0.5}')
mg.GetYaxis().SetTitle('{}_{#Lambda}^{3}H/#Lambda')







zero = np.array([0], dtype=np.float64)




ppb_stat040 = ROOT.TGraphErrors(1,x_pPb040,hp_ratio_040,zero,hp_ratiostat040)
ppb_stat040.SetLineColor(kVioletC)
ppb_stat040.SetMarkerColor(kVioletC)
ppb_stat040.SetMarkerStyle(20)
ppb_stat040.SetMarkerSize(0.5)

ppb_syst040 = ROOT.TGraphErrors(1,x_pPb040, hp_ratio_040, xe_pPb040, hp_ratiosyst040)
ppb_syst040.SetTitle("ALICE Internal p-Pb, 0-40%, #sqrt{#it{s}_{NN}}=5.02 TeV")
ppb_syst040.SetLineColor(kVioletC)
ppb_syst040.SetMarkerColor(kVioletC)
ppb_syst040.SetFillStyle(0)
ppb_syst040.SetMarkerStyle(20)
ppb_syst040.SetMarkerSize(0.5)


leg = ROOT.TLegend(0.55,0.4,0.88,0.5)
leg.SetMargin(0.14)

ppb_stat040.Draw("Pz")
ppb_syst040.Draw("P2")
leg.AddEntry(ppb_syst040,"","pf")



leg.SetEntrySeparation(0.2)
legT = ROOT.TLegend(0.55,0.18,0.88,0.38)
legT.SetMargin(0.14)

legT.AddEntry(hp_3body)
legT.AddEntry(hp_2body)
legT.AddEntry(hp_ratio_csm_1)
legT.AddEntry(hp_ratio_csm_3)
# legT.AddEntry(hp_ratio_csm_van)
leg.SetFillStyle(0)
legT.SetFillStyle(0)
leg.Draw()
legT.Draw()

pinfo = ROOT.TPaveText(0.7,0.63,0.82,0.73, 'NDC')
pinfo.SetBorderSize(0)
pinfo.SetFillStyle(0)
pinfo.SetTextAlign(30+3)
pinfo.SetTextFont(42)
pinfo.AddText('B.R. = 0.25')
pinfo.Draw()

cv.Draw()

cv.SaveAs("../Results/hp_ratio.pdf")
cv.SaveAs("../Results/hp_ratio.png")

# Branching ratio plot
cvBR = ROOT.TCanvas("brPlot","BR Plot",700,800)
cvBR.SetTopMargin(0.15)
cvBR.SetLeftMargin(0.15)
cvBR.SetRightMargin(0.04)
frame = cvBR.DrawFrame(0.14,7.e-8, 0.36, 1.4e-6, ";B.R.;{}_{#Lambda}^{3}H/#Lambda #times B.R.")
frame.GetYaxis().SetTitleOffset(1.3)
cvBR.SetLogy()

npoints = 50
xBR = np.linspace(0.14,0.36,npoints)
C2 = 6.57e-7
C2e = 1.39e-7
C3 = 3.15e-7
C3e = 8.57e-8

CSM1 = 2.7026086005800812e-06
CSM3 = 4.667110436005044e-06
CSM = 0.5 * (CSM3 + CSM1)
CSMe = 0.5 * (CSM3 - CSM1)

grData = ROOT.TGraphErrors(2)
grData.SetPoint(0, 0., hp_ratio_040[0] * 0.25)
grData.SetPointError(0, 0., math.hypot(hp_ratiostat040[0], hp_ratiosyst040[0]) * 0.25)
grData.SetPoint(1, 1., hp_ratio_040[0] * 0.25)
grData.SetPointError(1, 0., math.hypot(hp_ratiostat040[0], hp_ratiosyst040[0]) * 0.25)
grData.SetLineColor(kRedC)
grData.SetLineWidth(2)
grData.SetFillColorAlpha(kRedC,0.571)
grData.SetTitle("ALICE p-Pb 0-40%")

grCSM = ROOT.TGraphErrors(npoints)
grCSM1 = ROOT.TGraph(npoints)
grCSM3 = ROOT.TGraph(npoints)
grC2 = ROOT.TGraphErrors(npoints)
grC3 = ROOT.TGraphErrors(npoints)
for i,j in enumerate(xBR) : 
  grC2.SetPoint(i, j, C2 * j)
  grC2.SetPointError(i, 0, C2e * j)
  grC3.SetPoint(i, j, C3 * j)
  grC3.SetPointError(i, 0, C3e * j)
  grCSM1.SetPoint(i, j, CSM1 * j)
  grCSM3.SetPoint(i, j, CSM3 * j)
  grCSM.SetPoint(i, j, CSM * j)
  grCSM.SetPointError(i, 0, CSMe * j)

grC2.SetLineColor(kBlueC)
grC2.SetMarkerColor(kBlueC)
grC2.SetFillColorAlpha(kBlueC, 0.571)
grC2.SetTitle("2-body coalescence")
grC3.SetLineColor(kAzureC)
grC3.SetMarkerColor(kAzureC)
grC3.SetFillColorAlpha(kAzureC, 0.571)
grC3.SetTitle("3-body coalescence")
grCSM.SetLineColor(kGreyC)
grCSM.SetFillColorAlpha(kGreyC, 0.571)
grCSM.SetMarkerColor(kGreyC)
grCSM1.SetLineWidth(2)
grCSM1.SetTitle("CSM with T = 155MeV, Vc = dV/dy")
grCSM3.SetLineWidth(2)
grCSM3.SetLineStyle(ROOT.kDashed)
grCSM3.SetTitle("CSM with T = 155MeV, Vc = 3dV/dy")

grC2.Draw("PL3")
grC3.Draw("PL3")
# grCSM.Draw("P3")
grCSM3.Draw("L")
grCSM1.Draw("L")
grData.Draw("L3")

legBR = ROOT.TLegend(0.15,0.851 ,0.96,0.99)
legBR.SetNColumns(2)
legBR.SetMargin(0.2)
legBR.SetFillStyle(0)
legBR.AddEntry(grC2)
legBR.AddEntry(grCSM1)
legBR.AddEntry(grC3)
legBR.AddEntry(grCSM3)
legBR.AddEntry(grData)
legBR.Draw()

cvBR.SaveAs("plotBR.pdf")

file = ROOT.TFile('hp_ratio.root', 'recreate')
cv.Write()
cvBR.Write()
file.Close()