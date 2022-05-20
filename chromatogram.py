def make_normalized_chromatogram(self, drug, name):
    svgs = sb.NormalChroms(name)

    fwhm = self.rdata[drug]['max fwhm']
    arrt = self.rdata[drug]['avg rrt']
    art = self.rdata[drug]['avg rt']
    airt = art / arrt

    # Find Max Peak in Cals
    drt = 2 * fwhm
    ymax = 0
    xmin = (art - drt) / airt
    xmax = (art + drt) / airt

    yp = str(100 * (1 - 1 / p.mult)) + '%'
    xp = str(50 + (100 * arrt * 0.02 / drt)) + '%'
    svgs.add_line(xp, yp, xp, '100%')
    xp = str(50 - (100 * arrt * 0.02 / drt)) + '%'
    svgs.add_line(xp, yp, xp, '100%')

    for inj in self.rdata[drug]['cals'].values():
        cal = inj['chrom-target']
        if ymax < cal.ymax:
            ymax = cal.ymax

    for inj in self.rdata[drug]['cals'].values():
        cal = inj['chrom-target']
        rt = inj['rt']
        rrt = inj['rrt']

        if rt is not None and rrt is not None:
            irt = rt / rrt
            body = cal.get_body(xmin * irt, cal.ymin, xmax * irt, ymax, divx=irt)
            svgs.add_calibrator(0, p.chrom_y, body)

    # Sample
    inj = self.rdata[drug]['smpls'][name]
    smpl = inj['chrom-target']
    rt = inj['rt']
    rrt = inj['rrt']
    if rt is not None and rrt is not None:
        irt = rt / rrt
        body = smpl.get_body(xmin * irt, smpl.ymin, xmax * irt, smpl.ymax, divx=irt)
        svgs.add_sample(0, p.chrom_y, body)

    return svgs