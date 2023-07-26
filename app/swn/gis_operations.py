
with rasterio.open(
    '././app/geodata/buek_vektor/buek200_4326.tif', 'w',
    driver='GTiff',
    dtype=rasterio.uint8,
    count=1,
    width=shape[0],
    height=shape[1],
    transform=transform
) as dst:
    dst.write(rasterize_buek, indexes=1)