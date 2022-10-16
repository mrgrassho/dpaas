
# Análisis de los sitios seleccionados

A continuación listamos los sitios seleccionados:

- [Pañales online](https://www.panalesonline.com.ar/panales/bebes/)
- [Mundo Pañal](https://xn--elmundodelpaal-1nb.com.ar/#!/categoria/33/pagina/0/)
- [Pañalera Delta](https://panaleradelta.com.ar/product-category/panales-de-bebes/)
- [Todo en Pañales](https://www.todoenpa%C3%B1ales.com.ar/bebes/panales1)
- [La pañalera en casa](https://www.lapanaleraencasa.com.ar/bebe/panales)
- [Tienda L&S](https://www.tiendalys.com.ar/panales-de-bebe/)
- [Pañalera todo en Pañales](https://paaleratodoenpaales.mercadoshops.com.ar/listado/bebes/)
- [Pañalera Matlu](https://www.panaleramatlu.com.ar/panales-bebes/)
- [Pañalera DO RE MI](https://www.panaleradoremi.com.ar/panales/bebes/)
- [Pañalera - Travesuras](https://travesurasonline.sed.com.ar/catalogo;r=pa%C3%B1al%20bebe;s=pa%C3%B1al%20bebe;clear=true)
- [La pañalera escondida](https://www.lapañaleraescondida.com.ar/panales-para-bebes/)
- [Coto](https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-perfumer%C3%ADa-pa%C3%B1ales-y-productos-para-incontinencia-pa%C3%B1ales-para-beb%C3%A9/_/N-fmf3uu)
- [Jumbo](https://www.jumbo.com.ar/bebes-y-ninos/panales)
- [Carrefour](https://www.carrefour.com.ar/mundo-bebe/panales)
- [Mercado Libre](https://listado.mercadolibre.com.ar/panalera)

TO-DO:
- https://www.pañalesoeste.com.ar/producto/10-off-en-pampers-splashers-x-2-paquetes-iguales/
- https://www.hipermania.com.ar/producto/promo-2-hiperpacks-panales-pampers-premium-care-talle-xxg-extra-extra-grande-x54/
- https://www.gerlero.com.ar/bebes/panales.html
- https://emama.com.ar/categoria-producto/panales/
- https://drimel.com.ar/categoria/panales/bebes/page/14/
- https://www.babylandianqn.com.ar/#!/categoria/127/pagina/0/
- https://distribuidorajj.com.ar/product-category/panales/ninos/

## Descripción de Features

### Talles

Los talles se consideran que estan mostrados de forma *normal*, si se encuentran señalados en la descripción. Siguiendo la siguiente expresión regular:

```python
brand = "(?P<brand>huggies|pampers|babysec)"
size = "\s(pr|rn|p|m|g|xg|xxg)*\s*(\\\/|\-)*\s*(?P<size>pr|rn|p|m|g|xg|xxg)"
units_label_1 = "x\s*(?P<units>[0-9]+)"
units_label2 = "\[(?P<units>[0-9]+)\s*uni.\]"
DIAPERS_REGEX = [
    f".*{brand}.*{size}.*{units_label_1}",
    f".*{brand}.*{size}.*{units_label2}",
]
```

## [Pañales online](https://www.panalesonline.com.ar/panales/bebes/)

- **Talles**. No tiene talles en la descripcion. Se obtienen de un JSON.
- **Paginación**. El paginado es dinámico a medida que se scrollea.
- **E-commerce**: Tienda Nube.

## [Mundo Pañal](https://xn--elmundodelpaal-1nb.com.ar/#!/categoria/33/pagina/0/)

- **Inicialización**. Se tiene q comenzar por obtener las primeras tres pantallas de marcas.
  - PAMPERS - https://xn--elmundodelpaal-1nb.com.ar/#!/categoria/33/pagina/0/
  - HUGGIES - https://xn--elmundodelpaal-1nb.com.ar/#!/categoria/31/pagina/0/
  - BABYSEC - https://xn--elmundodelpaal-1nb.com.ar/#!/categoria/41/pagina/0/
- **Talles**. Algunos items no tienen talles en la descripcion. Se debe entrar manualmente item por item para obtener los talles de un dropdown en la página.
- **Paginación**. Se obtiene de manera normal con un 'siguiente' al final de página.

## [Pañalera Delta](https://panaleradelta.com.ar/product-category/panales-de-bebes/)

- **Inicialización**. Normal.
- **Talles**. Normal.
- **Paginación**. Se obtiene de manera normal con un 'siguiente' al final de página.

Atributos extraidos para cada item:

```python
>>> item = response.xpath('//div[contains(@class, "product-small")]')[0]
>>> item.xpath(".//p[contains(@class, 'product-title')]/a/text()").get()
'Pampers Premium Care Xxg Hpg x54'
>>> item.xpath(".//bdi/text()").get()
'3.470'
>>> item.xpath(".//p[contains(@class, 'product-title')]/a/@href").get()
'https://panaleradelta.com.ar/product/80681490-pampers-premium-care-xxg-hpg-54-x-02/'
>>> item.xpath(".//div[contains(@class, 'box-image')]//img/@src").get()
'https://panaleradelta.com.ar/wp-content/uploads/2021/05/thumbnail-8-300x300.jpg'
```

Paginado link:

```python
>>> response.xpath('//a[contains(@class, "next")]/@href').get()
'https://panaleradelta.com.ar/product-category/panales-de-bebes/page/2/'
```

Agregar limpieza de talles.

- Reemplazar [`gde`, `gd`, `grande`] por `g`
- Reemplazar [`med`, `mediano`] por `m`
- Reemplazar [`peq`, `pequeño`] por `g`
- Reemplazar [`xl`] por `xg`
- Reemplazar [`xtr `, `extra `] por `x`

## [Todo en Pañales](https://www.xn--todoenpaales-hhb.com.ar/bebes/panales1/)

- **Inicialización**. Normal.
- **Talles**. Normal en algunos casos. Muchos tienen los talles dentro de un modal.
- **Paginación**. El paginado es dinámico a medida que se scrollea.
- **E-commerce**: Tienda Nube - prefixtdp.mitiendanube.com

## [La pañalera en casa](https://www.lapanaleraencasa.com.ar/bebe/panales)

- **Talles**. No tiene talles en la descripcion. Se obtienen de un JSON.
- **Paginación**. El paginado es dinámico a medida que se scrollea.
- **E-commerce**: Tienda Nube.

## [Tienda L&S](https://www.tiendalys.com.ar/panales-de-bebe/)

- **Talles**. No tiene talles en la descripcion. Se obtienen de un JSON.
- **Paginación**. El paginado es dinámico a medida que se scrollea.
- **E-commerce**: Tienda Nube.

## [Pañalera todo en Pañales](https://paaleratodoenpaales.mercadoshops.com.ar/listado/bebes/)

- **Talles**. Normal.
- **Paginación**. Se obtiene de manera normal con un 'siguiente' al final de página.
- **E-commerce**: Mercado Shops.

## [Pañalera Matlu](https://www.panaleramatlu.com.ar/panales-bebes/)

- **Talles**. Normal.
- **Paginación**. Se obtiene de manera normal con un 'siguiente' al final de página.
- **E-commerce**: Tienda Nube.

## [Pañalera DO RE MI](https://www.panaleradoremi.com.ar/panales/bebes/)

- **Talles**. Normal.
- **Paginación**. Se obtiene de manera normal con un 'siguiente' al final de página.
- **E-commerce**: Tienda Nube.

## [Pañalera - Travesuras](https://travesurasonline.sed.com.ar/catalogo;r=pa%C3%B1al%20bebe;s=pa%C3%B1al%20bebe;clear=true)

- **Talles**. Normal.
- **Paginación**. Se obtiene de manera normal con un 'siguiente' al final de página.
- **E-commerce**: -

## [La pañalera escondida](https://www.xn--lapaaleraescondida-q0b.com.ar/panales-para-bebes/)

- **Talles**. Algunos no tienen talles en la descripcion. Se obtienen de un JSON.
- **Paginación**. El paginado es dinámico a medida que se scrollea.
- **E-commerce**: Tienda Nube.

## [Coto](https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-perfumer%C3%ADa-pa%C3%B1ales-y-productos-para-incontinencia-pa%C3%B1ales-para-beb%C3%A9/_/N-fmf3uu)

- **Talles**. Normal.
- **Paginación**. Se obtiene de manera normal con un 'siguiente' al final de página.
- **E-commerce**: -

## [Jumbo](https://www.jumbo.com.ar/bebes-y-ninos/panales)

- **Talles**. Normal.
- **Paginación**. El paginado es dinámico a medida que se scrollea.
- **E-commerce**: -

## [Carrefour](https://www.carrefour.com.ar/mundo-bebe/panales)

- **Talles**. Normal.
- **Paginación**. Se obtiene de manera normal con un 'siguiente' al final de página.
- **E-commerce**: -

## [Mercado Libre](https://listado.mercadolibre.com.ar/panalera)

- **Talles**. Puede ser engañoso porque cada item tiene el talle en la descripción pero el verdadero talle se encuentra en la publicación donde puede haber mas de un talle y cantidad por item.
- **Paginación**. Se obtiene de manera normal con un 'siguiente' al final de página.
- **E-commerce**: -

## E-commerces

### Tienda Nube

Todos los talles de este e-commerce se encuentra en un tag `data-installments`

```json
[
  {
    "product_id": 123056300,
    "price_short": "$3.670",
    "price_long": "$3.670 ARS",
    "price_number": 3670,
    "compare_at_price_short": null,
    "compare_at_price_long": null,
    "compare_at_price_number": null,
    "stock": 2,
    "sku": null,
    "available": true,
    "contact": false,
    "option0": "L",
    "option1": null,
    "option2": null,
    "id": 479450037,
    "image": 327794945,
    "image_url": "//d3ugyf2ht6aenh.cloudfront.net/stores/808/715/products/d_nq_np_2x_949594-mla45187277620_032021-f1-054f1c41626cddce3d16547895797882-1024-1024.jpg",
    "installments_data": "{\"mercadopago\":{\"1\":{\"installment_value\":3670,\"installment_value_cents\":367000,\"interest\":0,\"total_value\":3670,\"without_interests\":true},\"3\":{\"installment_value\":1543.235,\"installment_value_cents\":154323.5,\"interest\":0.2615,\"total_value\":4629.705,\"without_interests\":false},\"6\":{\"installment_value\":907.4075,\"installment_value_cents\":90740.75,\"interest\":0.4835,\"total_value\":5444.445,\"without_interests\":false},\"9\":{\"installment_value\":712.91788888889,\"installment_value_cents\":71291.788888889,\"interest\":0.7483,\"total_value\":6416.261,\"without_interests\":false},\"12\":{\"installment_value\":623.86941666667,\"installment_value_cents\":62386.941666667,\"interest\":1.0399,\"total_value\":7486.433,\"without_interests\":false},\"18\":{\"installment_value\":540.91722222222,\"installment_value_cents\":54091.722222222,\"interest\":1.653,\"total_value\":9736.51,\"without_interests\":false},\"24\":{\"installment_value\":508.58554166667,\"installment_value_cents\":50858.554166667,\"interest\":2.3259,\"total_value\":12206.053,\"without_interests\":false}}}"
  },
  {
    "product_id": 123056300,
    "price_short": "$3.670",
    "price_long": "$3.670 ARS",
    "price_number": 3670,
    "compare_at_price_short": null,
    "compare_at_price_long": null,
    "compare_at_price_number": null,
    "stock": 0,
    "sku": null,
    "available": false,
    "contact": false,
    "option0": "XXL",
    "option1": null,
    "option2": null,
    "id": 479450038,
    "image": 327794750,
    "image_url": "//d3ugyf2ht6aenh.cloudfront.net/stores/808/715/products/xxg-x521-a12d4738d5d00b1a5a16547895797802-1024-1024.jpg",
    "installments_data": "{\"mercadopago\":{\"1\":{\"installment_value\":3670,\"installment_value_cents\":367000,\"interest\":0,\"total_value\":3670,\"without_interests\":true},\"3\":{\"installment_value\":1543.235,\"installment_value_cents\":154323.5,\"interest\":0.2615,\"total_value\":4629.705,\"without_interests\":false},\"6\":{\"installment_value\":907.4075,\"installment_value_cents\":90740.75,\"interest\":0.4835,\"total_value\":5444.445,\"without_interests\":false},\"9\":{\"installment_value\":712.91788888889,\"installment_value_cents\":71291.788888889,\"interest\":0.7483,\"total_value\":6416.261,\"without_interests\":false},\"12\":{\"installment_value\":623.86941666667,\"installment_value_cents\":62386.941666667,\"interest\":1.0399,\"total_value\":7486.433,\"without_interests\":false},\"18\":{\"installment_value\":540.91722222222,\"installment_value_cents\":54091.722222222,\"interest\":1.653,\"total_value\":9736.51,\"without_interests\":false},\"24\":{\"installment_value\":508.58554166667,\"installment_value_cents\":50858.554166667,\"interest\":2.3259,\"total_value\":12206.053,\"without_interests\":false}}}"
  },
  {
    "product_id": 123056300,
    "price_short": "$3.670",
    "price_long": "$3.670 ARS",
    "price_number": 3670,
    "compare_at_price_short": null,
    "compare_at_price_long": null,
    "compare_at_price_number": null,
    "stock": 4,
    "sku": null,
    "available": true,
    "contact": false,
    "option0": "XL",
    "option1": null,
    "option2": null,
    "id": 479450040,
    "image": 327794599,
    "image_url": "//d3ugyf2ht6aenh.cloudfront.net/stores/808/715/products/xg-x521-1b812341fa0e6b0ce616547895797703-1024-1024.jpg",
    "installments_data": "{\"mercadopago\":{\"1\":{\"installment_value\":3670,\"installment_value_cents\":367000,\"interest\":0,\"total_value\":3670,\"without_interests\":true},\"3\":{\"installment_value\":1543.235,\"installment_value_cents\":154323.5,\"interest\":0.2615,\"total_value\":4629.705,\"without_interests\":false},\"6\":{\"installment_value\":907.4075,\"installment_value_cents\":90740.75,\"interest\":0.4835,\"total_value\":5444.445,\"without_interests\":false},\"9\":{\"installment_value\":712.91788888889,\"installment_value_cents\":71291.788888889,\"interest\":0.7483,\"total_value\":6416.261,\"without_interests\":false},\"12\":{\"installment_value\":623.86941666667,\"installment_value_cents\":62386.941666667,\"interest\":1.0399,\"total_value\":7486.433,\"without_interests\":false},\"18\":{\"installment_value\":540.91722222222,\"installment_value_cents\":54091.722222222,\"interest\":1.653,\"total_value\":9736.51,\"without_interests\":false},\"24\":{\"installment_value\":508.58554166667,\"installment_value_cents\":50858.554166667,\"interest\":2.3259,\"total_value\":12206.053,\"without_interests\":false}}}"
  }
]
```

### Sitios Tienda Nube:
  - https://tienda-nube-ecommerce.com/panales/bebes
  - https://www.xn--todoenpaales-hhb.com.ar/bebes/panales1
  - https://www.panalesonline.com.ar/panales/bebes
  - https://www.lapanaleraencasa.com.ar/bebe/panales
  - https://www.tiendalys.com.ar/panales-de-bebe
  - https://www.panaleramatlu.com.ar/panales-bebes
  - https://www.panaleradoremi.com.ar/panales/bebes
  - https://www.xn--lapaaleraescondida-q0b.com.ar/panales-para-bebes
  - https://panalonce.com.ar/panales/bebes
  - https://www.parquepanial.com.ar/panales-de-bebe
  - https://www.anaperfumeriaonline.com.ar/panales/panales-bebe
  - https://www.panolino.com.ar/bebes/oleos
  - https://www.vmdecompras.com.ar/recien-nacido
  - https://www.perfumeriasmiriam.com/bebes-y-maternidad1/panales
  - https://www.noninoni.com.ar/panales/bebes
  - https://www.morashop.ar/todo-para-tu-bebe/higiene-y-cuidado-del-bebe/panales
  - https://piquilines.com.ar/rn
  - https://www.xn--tiendamipaal-jhb.com.ar/panales
  - https://www.panalerananita.com.ar/panales