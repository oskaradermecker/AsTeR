# Author:  DINDIN Meryll
# Date:    04 May 2019
# Project: AsTeR

try: from process.apis import *
except: from apis import *

class Weather:

    def __init__(self, grid):

        self.grid = np.load(grid)

    def aggregate(self, date):

        dtf = []

        for latitude, longitude in tqdm.tqdm(self.grid.astype(str)):
            req = Meteo_Sky().request(longitude, latitude, date)
            arg = {'columns': ['longitude', 'latitude']}
            crd = pd.DataFrame([[longitude, latitude] for _ in range(req.shape[0])], **arg)
            crd.index = req.index
            dtf.append(pd.concat([req, crd], axis=1))

        return pd.concat(dtf).astype('float32')

    def wind_arrows(self, dtf):
    
        arrows = folium.FeatureGroup('Wind Arrows')

        def define_arrow(point, speed, bearing):

            end_point = [np.cos(bearing)*speed + point[0], np.sin(bearing)*speed + point[1]]
            tail = folium.PolyLine(locations=[point, end_point], color='black')
            arg = {'number_of_sides': 3, 'radius': 3, 'rotation': int(bearing)}
            head = folium.RegularPolygonMarker(location=tuple(end_point), color='black', **arg)

            return tail, head

        tmp = dtf[dtf.index == dtf.index[0]]
        msk = ['longitude', 'latitude', 'windSpeed', 'windBearing']
        for longitude, latitude, speed, bearing in tmp[msk].values:
            tail, head = define_arrow([float(latitude), float(longitude)], float(speed)/200, float(bearing))
            tail.add_to(arrows)
            head.add_to(arrows)
            
        return arrows

    def contour_plot(self, dtf, feature):
        
        group = folium.FeatureGroup('Contours {}{}'.format(feature[0].upper(), feature[1:]))
        
        x_orig = np.asarray(dtf.longitude.tolist())
        y_orig = np.asarray(dtf.latitude.tolist())
        z_orig = np.asarray(dtf[feature].tolist())

        x_arr = np.linspace(np.min(x_orig)-0.5, np.max(x_orig)+0.5, 1000)
        y_arr = np.linspace(np.min(y_orig)-0.5, np.max(y_orig)+0.5, 1000)
        xm,ym = np.meshgrid(x_arr, y_arr)
        zmesh = griddata((x_orig, y_orig), z_orig, (xm, ym), method='linear')
        zmesh = sp.ndimage.filters.gaussian_filter(zmesh, [5, 5], mode='constant')

        vmin, vmax = dtf[feature].min(), dtf[feature].max()
        colors = ['#d7191c',  '#fdae61',  '#ffffbf',  '#abdda4',  '#2b83ba']
        cm = branca.colormap.LinearColormap(colors, vmin=vmin, vmax=vmax).to_step(len(colors))
        cm.caption = '{}{}'.format(feature[0].upper(), feature[1:])
        arg = {'alpha': 0.5, 'colors': colors, 'linestyles': 'None'}
        contourf = plt.contourf(xm, ym, zmesh, len(colors), vmin=vmin, vmax=vmax, **arg)
        plt.clf()

        arg = {'min_angle_deg': 3.0, 'ndigits': 5, 'stroke_width': 1, 'fill_opacity': 0.5}
        geojson = geojsoncontour.contourf_to_geojson(contourf=contourf, **arg)

        folium.GeoJson(geojson, style_function=lambda x: {
            'color': x['properties']['stroke'], 'weight': x['properties']['stroke-width'],
            'fillColor': x['properties']['fill'], 'opacity': 0.6}).add_to(group)
        group.add_child(cm)
        
        return group
