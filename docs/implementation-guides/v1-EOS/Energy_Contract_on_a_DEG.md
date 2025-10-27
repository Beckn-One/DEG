# Implementation Guide

This document contains the REQUIRED and RECOMMENDED standard functionality that must be implemented by any Energy Producer Platform a.k.a BPPs and Energy Consumer Platforms a.k.a BAPs.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC2119](https://datatracker.ietf.org/doc/html/rfc2119) from IETF.

## 5.1 Discovery of Energy Sources

### 5.1.1 Recommendations for BPPs

The following recommendations need to be considered when implementing discovery functionality for an Energy Provider BPP

- REQUIRED. The BPP MUST implement the `search` endpoint to receive an `Intent` object sent by BAPs
- REQUIRED. The BPP MUST return a catalog of energy sources on the `on_search` callback endpoint specified in the `context.bpp_uri` field of the `search` request body.
- REQUIRED. The BPP MUST map its energy source to the `Item` schema.
- REQUIRED. Any energy provider-related information like name, logo, short description must be mapped to the `Provider.descriptor` schema
- REQUIRED. If the BPP wants to group its energy sources under a specific category, it must map each category to the `Category` schema
- REQUIRED. Any energy transfer related information MUST be mapped to the `Fulfillment` schema.
- REQUIRED. If the BPP does not want to respond to a search request, it MUST return a `ack.status` value equal to `NACK`
- RECOMMENDED. Upon receiving a `search` request, the BPP SHOULD return a catalog that best matches the intent. This can be done by indexing the catalog against the various probable paths in the `Intent` schema relevant to typical financial service use cases

### 5.1.2 Recommendations for BAPs

- REQUIRED. The BAP MUST call the `search` endpoint of the BG to discover multiple BPPs on a network
- REQUIRED. The BAP MUST implement the `on_search` endpoint to consume the `Catalog` objects containing Energy Sources sent by BPPs.
- REQUIRED. The BAP MUST expect multiple catalogs sent by the respective Energy Providers on the network
- REQUIRED. The energy sources can be found in the `Catalog.providers[].items[]` array in the `on_search` request
- REQUIRED. If the `catalog.providers[].items[].xinput` object is present, then the BAP MUST redirect the user to, or natively render the form present on the link specified on the `items[].xinput.form.url` field.
- REQUIRED. If the `catalog.providers[].items[].xinput.required` field is set to `"true"` , then the BAP MUST NOT fire a `select`, `init` or `confirm` call until the form is submitted and a successful response is received
- RECOMMENDED. If the `catalog.providers[].items[].xinput.required` field is set to `"false"` , then the BAP SHOULD allow the user to skip filling the form

### Example

The search is broadcast to all providers on the network, there will be many providers. The providers could be EV chargers, Discoms or Energy Aggregators. The search request can look something like this.

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "search",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "intent": {
      "category": {
        "descriptor": {
          "code": "green-tariff"
        }
      },
      "item": {
        "descriptor": {
          "code": "energy"
        },
        "quantity": {
          "available": {
            "measure": {
              "unit": "kWH",
              "value": "4.0"
            }
          }
        }
      },
      "location": {
        "circle": {
          "gps": "12.423423,77.325647",
          "radius": {
            "type": "CONSTANT",
            "value": "5",
            "unit": "km"
          }
        }
      }
    }
  }
}
```

The on_search comes from all the providers, The providers have to be mapped to the provider schema. The `on_search` would look like this.

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "on_search",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "example-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "catalog": {
      "providers": [
        {
          "id": "chargezone.in",
          "descriptor": {
            "name": "Chargezone",
            "short_desc": "Chargezone Technologies Pvt Ltd",
            "images": [
              {
                "url": "https://chargezone.in/images/logo.png"
              }
            ]
          },
          "locations": [
            {
              "id": "1",
              "gps": "12.345345,77.389754"
            },
            {
              "id": "2",
              "gps": "12.247934,77.876987"
            }
          ],
          "categories": [
            {
              "id": "1",
              "descriptor": {
                "code": "green-tariff",
                "name": "green tariff"
              }
            }
          ],
          "fulfillments": [
            {
              "id": "1",
              "type": "CHARGING",
              "stops": [
                {
                  "type": "start",
                  "time": {
                    "timestamp": "01-06-2023 10:00:00"
                  }
                },
                {
                  "type": "end",
                  "time": {
                    "timestamp": "01-06-2023 10:30:00"
                  }
                }
              ],
              "tags": [
                {
                  "descriptor": {
                    "name": "Charging Point Specifications"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "name": "Charger type",
                        "code": "charger-type"
                      },
                      "value": "AC"
                    },
                    {
                      "descriptor": {
                        "name": "Connector type",
                        "code": "connector-type"
                      },
                      "value": "CCS2"
                    },
                    {
                      "descriptor": {
                        "name": "Power Rating"
                      },
                      "value": "greater than 50kW"
                    },
                    {
                      "descriptor": {
                        "name": "Availability"
                      },
                      "value": "Available"
                    }
                  ],
                  "display": true
                }
              ]
            },
            {
              "id": "2",
              "type": "CHARGING",
              "stops": [
                {
                  "type": "start",
                  "time": {
                    "timestamp": "01-06-2023 10:00:00"
                  }
                },
                {
                  "type": "end",
                  "time": {
                    "timestamp": "01-06-2023 10:30:00"
                  }
                }
              ],
              "tags": [
                {
                  "descriptor": {
                    "name": "Charging Point"
                  },
                  "list": [
                    {
                      "descriptor": {
                        "name": "Charger type"
                      },
                      "value": "AC"
                    },
                    {
                      "descriptor": {
                        "name": "Connector type"
                      },
                      "value": "CCS2"
                    },
                    {
                      "descriptor": {
                        "name": "Power Rating"
                      },
                      "value": "greater than 50kW"
                    },
                    {
                      "descriptor": {
                        "name": "Availability"
                      },
                      "value": "Available"
                    }
                  ],
                  "display": true
                }
              ]
            }
          ],
          "items": [
            {
              "id": "pe-charging-01",
              "descriptor": {
                "code": "energy"
              },
              "price": {
                "value": "8",
                "currency": "INR/kWH"
              },
              "quantity": {
                "available": {
                  "measure": {
                    "unit": "kWH",
                    "value": "100"
                  }
                }
              },
              "category_ids": [
                "1"
              ],
              "location_ids": [
                "1",
                "2"
              ],
              "fulfillment_ids": [
                "1",
                "2"
              ],
              "add_ons": [
                {
                  "id": "pe-charging-01-addon-1",
                  "descriptor": {
                    "name": "Free car wash"
                  },
                  "price": {
                    "value": "0",
                    "currency": "INR"
                  }
                }
              ]
            }
          ]
        },
        {
          "id": "log9.in",
          "descriptor": {
            "name": "Log9 Inc"
          },
          "categories": [
            {
              "id": "1",
              "descriptor": {
                "code": "green-tariff",
                "name": "green tariff"
              }
            }
          ],
          "fulfillments": [
            {
              "id": "3",
              "type": "BATTERY-SWAP",
              "stops": [
                {
                  "location": {
                    "gps": "12.745675, 77.987393"
                  }
                }
              ]
            },
            {
              "id": "4",
              "type": "MOBILE-BATTERY-SWAP",
              "stops": [
                {
                  "location": {
                    "url": "https://log9.in/track/bswap/3234242"
                  }
                }
              ]
            }
          ],
          "items": [
            {
              "id": "pe-charging-01",
              "descriptor": {
                "code": "energy"
              },
              "price": {
                "value": "10",
                "currency": "INR / kWH"
              },
              "quantity": {
                "available": {
                  "measure": {
                    "unit": "kWH",
                    "value": "1000"
                  }
                }
              },
              "category_ids": [
                "1"
              ],
              "fulfillment_ids": [
                "3",
                "4"
              ],
              "add_ons": [
                {
                  "id": "pe-charging-01-addon-1",
                  "descriptor": {
                    "name": "Free tyre pressure check"
                  },
                  "price": {
                    "value": "0",
                    "currency": "INR"
                  }
                }
              ]
            }
          ]  
        }
      ]
    }
  }
}
```

## Ordering

This section provides recommendations for implementing the APIs related to creating an order for energy.

### 5.2.1 Recommendations for BPPs

#### 5.2.1.1 Selecting a service from the catalog

- REQUIRED. The BPP MUST implement the `select` endpoint on the url specified in URL specified in the `context.bpp_uri` field sent during `on_search`. In case of permissioned networks, this URL MUST match the `Subscriber.url` present on the respective entry in the Network Registry
- REQUIRED. The BPP MUST check for a form submission at the URL specified on the `xinput.form.url` before acknowledging a `select` request.
- REQUIRED. If the energy service provider has successfully received the information submitted by the energy service consumer, the BPP must return an acknowledgement with `ack.status` set to `ACK` in response to the `select` request
- REQUIRED. If the energy service provider has returned a successful acknowledgement to a `select` request, it MUST send the offer encapsulated in an `Order` object

#### 5.2.1.2 Initializing an order for an energy related service

- REQUIRED. The BPP MUST implement the `init` endpoint on the url specified in URL specified in the `context.bpp_uri` field sent during `on_search`. In case of permissioned networks, this URL MUST match the `Subscriber.url` present on the respective entry in the Network Registry

#### 5.2.1.3 Confirming an order for an energy related service

- REQUIRED. The BPP MUST implement the `confirm` endpoint on the url specified in URL specified in the `context.bpp_uri` field sent during `on_search`. In case of permissioned networks, this URL MUST match the `Subscriber.url` present on the respective entry in the Network Registry

### 5.2.2 Recommendations for BAPs

#### 5.2.2.1 Selecting a financial service from the catalog

#### 5.2.2.2 Initializing an order for a energy service

#### 5.2.2.3 Confirming the order for the energy service

### 5.2.3 Example Workflow

### 5.2.3 Example Requests

An example of `select` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "select",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "chargezone-energy-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order": {
      "provider": {
        "id": "chargezone.in"
      },
      "items": [
        {
          "id": "pe-charging-01",
          "quantity": {
            "selected": {
              "measure": {
                "value": "4",
                "unit": "kWh"
              }
            }
          },
          "add_ons": [
            {
              "id": "pe-charging-01-addon-1"
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "id": "1"
        }
      ]
    }
  }
}
```

An example of `on_select` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "on_select",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "example-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order": {
      "providers": {
        "id": "chargezone.in",
        "descriptor": {
          "name": "Chargezone",
          "short_desc": "Chargezone Technologies Pvt Ltd",
          "images": [
            {
              "url": "https://chargezone.in/images/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "pe-charging-01",
          "descriptor": {
            "code": "energy"
          },
          "price": {
            "value": "8",
            "currency": "INR/kWH"
          },
          "quantity": {
            "available": {
              "measure": {
                "value": "100",
                "unit": "kWh"
              }
            },
            "selected": {
              "measure": {
                "value": "4",
                "unit": "kWh"
              }
            }
          }
        },
        {
          "id": "pe-charging-01-addon-1",
          "descriptor": {
            "code": "add-on-item",
            "name": "Free car wash"
          },
          "price": {
            "value": "0",
            "currency": "INR"
          }
        }
      ],
      "fulfillments": [
        {
          "id": "1",
          "type": "CHARGING",
          "stops": [
            {
              "type": "start",
              "time": {
                "timestamp": "01-06-2023 10:00:00"
              }
            },
            {
              "type": "end",
              "time": {
                "timestamp": "01-06-2023 10:30:00"
              }
            }
          ],
          "tags": [
            {
              "descriptor": {
                "name": "Charging Point Specifications"
              },
              "list": [
                {
                  "descriptor": {
                    "name": "Charger type",
                    "code": "charger-type"
                  },
                  "value": "AC"
                },
                {
                  "descriptor": {
                    "name": "Connector type",
                    "code": "connector-type"
                  },
                  "value": "CCS2"
                },
                {
                  "descriptor": {
                    "name": "Power Rating"
                  },
                  "value": "greater than 50kW"
                },
                {
                  "descriptor": {
                    "name": "Availability"
                  },
                  "value": "Available"
                }
              ],
              "display": true
            }
          ]
        }
      ],
      "quote": {
        "price": {
          "value": "32",
          "currency": "INR"
        },
        "breakup": [
          {
            "item": {
              "id": "pe-charging-01",
              "descriptor": {
                "name": "Estimated units consumed"
              },
              "quantity": {
                "selected": {
                  "measure": {
                    "value": "4",
                    "unit": "kWh"
                  }
                }
              }
            },
            "price": {
              "value": "32",
              "currency": "INR"
            }
          },
          {
            "item": {
              "add-ons": [
                {
                  "id": "pe-charging-01-addon-1"
                }
              ],
              "descriptor": {
                "name": "Free car wash"
              }
            },
            "price": {
              "value": "0",
              "currency": "INR"
            }
          }
        ]
      }
    }
  }
}
```

An example of `init` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "init",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "chargezone-energy-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order": {
      "provider": {
        "id": "chargezone.in"
      },
      "items": [
        {
          "id": "pe-charging-01",
          "quantity": {
            "selected": {
              "measure": {
                "value": "4",
                "unit": "kWh"
              }
            }
          },
          "add_ons": [
            {
              "id": "pe-charging-01-addon-1"
            }
          ]
        }
      ],
      "billing": {
        "name": "John Doe",
        "email": "abc@example.com",
        "phone": "+91-9876522222"
      },
      "fulfillments": [
        {
          "id": "1",
          "customer": {
            "person": {
              "name": "John Doe"
            },
            "contact": {
              "phone": "+91-9887766554"
            }
          }
        }
      ]
    }
  }
}
```

An example of `on_init` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "on_init",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "example-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order": {
      "providers": {
        "id": "chargezone.in",
        "descriptor": {
          "name": "Chargezone",
          "short_desc": "Chargezone Technologies Pvt Ltd",
          "images": [
            {
              "url": "https://chargezone.in/images/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "pe-charging-01",
          "descriptor": {
            "code": "energy"
          },
          "price": {
            "value": "8",
            "currency": "INR/kWH"
          },
          "quantity": {
            "available": {
              "measure": {
                "value": "100",
                "unit": "kWh"
              }
            },
            "selected": {
              "measure": {
                "value": "4",
                "unit": "kWh"
              }
            }
          },
          "add_ons": [
            {
              "id": "pe-charging-01-addon-1",
              "descriptor": {
                "code": "add-on-item",
                "name": "Free car wash"
              },
              "price": {
                "value": "0",
                "currency": "INR"
              }
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "id": "1",
          "customer": {
            "person": {
              "name": "John Doe"
            },
            "contact": {
              "phone": "+91-9887766554"
            }
          },
          "type": "CHARGING",
          "state": {
            "descriptor": {
              "code": "order-initiated"
            }
          },
          "stops": [
            {
              "type": "start",
              "time": {
                "timestamp": "01-06-2023 10:00:00"
              }
            },
            {
              "type": "end",
              "time": {
                "timestamp": "01-06-2023 10:30:00"
              }
            }
          ],
          "tags": [
            {
              "descriptor": {
                "name": "Charging Point"
              },
              "list": [
                {
                  "descriptor": {
                    "name": "Charger type"
                  },
                  "value": "AC"
                },
                {
                  "descriptor": {
                    "name": "Connector type"
                  },
                  "value": "CCS2"
                },
                {
                  "descriptor": {
                    "name": "Power Rating"
                  },
                  "value": "greater than 50kW"
                },
                {
                  "descriptor": {
                    "name": "Availability"
                  },
                  "value": "Available"
                }
              ],
              "display": true
            }
          ]
        }
      ],
      "billing": {
        "email": "abc@example.com",
        "number": "+91-9876522222"
      },
      "quote": {
        "price": {
          "value": "32",
          "currency": "INR"
        },
        "breakup": [
          {
            "item": {
              "descriptor": {
                "name": "Estimated units consumed"
              },
              "quantity": {
                "selected": {
                  "measure": {
                    "value": "4",
                    "unit": "kWh"
                  }
                }
              }
            },
            "price": {
              "value": "32",
              "currency": "INR"
            }
          }
        ]
      },
      "payments": [
        {
          "url": "https://payment.gateway.in",
          "type": "PRE-ORDER",
          "status": "NOT-PAID",
          "params": {
            "amount": "40",
            "currency": "INR"
          },
          "time": {
            "range": {
              "start": "2023-08-10T10:00:00Z",
              "end": "2023-08-10T10:30:00Z"
            }
          }
        }
      ],
      "cancellation_terms": [
        {
          "fulfillment_state": {
            "descriptor": {
              "code": "charging-start"
            }
          },
          "cancellation_fee": {
            "percentage": "30%"
          },
          "external_ref": {
            "mimetype": "text/html",
            "url": "https://chargezone.in/charge/tnc.html"
          }
        }
      ]
    }
  }
}
```

An example of `confirm` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "confirm",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "chargezone-energy-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order": {
      "providers": {
        "id": "chargezone.in"
      },
      "items": [
        {
          "id": "pe-charging-01",
          "quantity": {
            "selected": {
              "measure": {
                "value": "4",
                "unit": "kWh"
              }
            }
          },
          "add_ons": [
            {
              "id": "pe-charging-01-addon-1"
            }
          ]
        }
      ],
      "billing": {
        "name": "John Doe",
        "email": "abc@example.com",
        "number": "+91-9876522222"
      },
      "fulfillments": [
        {
          "id": "1",
          "customer": {
            "person": {
              "name": "John Doe"
            },
            "contact": {
              "phone": "+91-9887766554"
            }
          }
        }
      ],
      "payments": [
        {
          "collected_by": "BPP",
          "params": {
            "amount": "40",
            "currency": "INR"
          },
          "status": "PAID",
          "type": "PRE-ORDER"
        }
      ],
      "quote": {
        "price": {
          "value": "40",
          "currency": "INR"
        },
        "breakup": [
          {
            "item": {
              "descriptor": {
                "name": "Estimated units consumed"
              },
              "quantity": {
                "selected": {
                  "measure": {
                    "value": "4",
                    "unit": "kWh"
                  }
                }
              }
            },
            "price": {
              "value": "32",
              "currency": "INR"
            }
          }
        ]
      }
    }
  }
}
```

An example of `on_confirm` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "on_confirm",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "example-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order": {
      "id": "6743e9e2-4fb5-487c-92b7",
      "providers": {
        "id": "chargezone.in",
        "descriptor": {
          "name": "Chargezone",
          "short_desc": "Chargezone Technologies Pvt Ltd",
          "images": [
            {
              "url": "https://chargezone.in/images/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "pe-charging-01",
          "descriptor": {
            "code": "energy"
          },
          "price": {
            "value": "8",
            "currency": "INR/kWH"
          },
          "quantity": {
            "available": {
              "measure": {
                "value": "100",
                "unit": "kWh"
              }
            },
            "selected": {
              "measure": {
                "value": "4",
                "unit": "kWh"
              }
            }
          },
          "add_ons": [
            {
              "id": "pe-charging-01-addon-1",
              "descriptor": {
                "code": "add-on-item",
                "name": "Free car wash"
              },
              "price": {
                "value": "0",
                "currency": "INR"
              }
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "id": "1",
          "customer": {
            "person": {
              "name": "John Doe"
            },
            "contact": {
              "phone": "+91-9887766554"
            }
          },
          "type": "CHARGING",
          "state": {
            "descriptor": {
              "code": "payment-completed"
            }
          },
          "stops": [
            {
              "type": "start",
              "location": {
                "gps": "12.423423,77.325647"
              },
              "time": {
                "timestamp": "01-06-2023 10:00:00",
                "range": {
                  "start": "01-06-2023 10:00:00",
                  "end": "01-06-2023 10:10:00"
                }
              },
              "instructions": {
                "name": "Charging instructions",
                "short_desc": "To start your charging, go to charger number 987, and click on 'start' on your app"
              }
            },
            {
              "type": "end",
              "time": {
                "timestamp": "01-06-2023 10:30:00",
                "range": {
                  "start": "01-06-2023 10:30:00",
                  "end": "01-06-2023 10:40:00"
                }
              }
            }
          ],
          "tags": [
            {
              "descriptor": {
                "name": "Charging Point"
              },
              "list": [
                {
                  "descriptor": {
                    "name": "Charger type"
                  },
                  "value": "AC"
                },
                {
                  "descriptor": {
                    "name": "Connector type"
                  },
                  "value": "CCS2"
                },
                {
                  "descriptor": {
                    "name": "Power Rating"
                  },
                  "value": "greater than 50kW"
                },
                {
                  "descriptor": {
                    "name": "Availability"
                  },
                  "value": "Available"
                }
              ],
              "display": true
            }
          ]
        }
      ],
      "billing": {
        "email": "abc@example.com",
        "number": "+91-9876522222"
      },
      "quote": {
        "price": {
          "value": "40",
          "currency": "INR"
        },
        "breakup": [
          {
            "item": {
              "descriptor": {
                "name": "Estimated units consumed"
              },
              "quantity": {
                "selected": {
                  "measure": {
                    "value": "4",
                    "unit": "kWh"
                  }
                }
              }
            },
            "price": {
              "value": "32",
              "currency": "INR"
            }
          }
        ]
      },
      "payments": [
        {
          "type": "PRE-ORDER",
          "status": "PAID",
          "params": {
            "amount": "40",
            "currency": "INR"
          },
          "time": {
            "range": {
              "start": "2023-08-10T10:00:00Z",
              "end": "2023-08-10T10:30:00Z"
            }
          }
        }
      ],
      "cancellation_terms": [
        {
          "fulfillment_state": {
            "descriptor": {
              "code": "charging-start"
            }
          },
          "cancellation_fee": {
            "percentage": "30%"
          },
          "external_ref": {
            "mimetype": "text/html",
            "url": "https://chargezone.in/charge/tnc.html"
          }
        }
      ]
    }
  }
}
```

## Fulfillment

This section contains recommendations for implementing the APIs related to fulfilling a energy service order

### 5.3.1 Recommendations for BPPs

#### 5.3.1.1 Sending status updates

- REQUIRED. The BPP MUST implement the `status` endpoint on the url specified in URL specified in the `context.bpp_uri` field sent during `on_search`. In case of permissioned networks, this URL MUST match the `Subscriber.url` present on the respective entry in the Network Registry

#### 5.3.1.2 Updating an order for energy service

- REQUIRED. The BPP MUST implement the `update` endpoint on the url specified in URL specified in the `context.bpp_uri` field sent during `on_search`. In case of permissioned networks, this URL MUST match the `Subscriber.url` present on the respective entry in the Network Registry

#### 5.3.1.3 Cancelling a energy service order

- REQUIRED. The BPP MUST implement the `cancel` endpoint on the url specified in URL specified in the `context.bpp_uri` field sent during `on_search`. In case of permissioned networks, this URL MUST match the `Subscriber.url` present on the respective entry in the Network Registry
- REQUIRED. The BPP MUST implement the `get_cancellation_reasons` endpoint on the url specified in URL specified in the `context.bpp_uri` field sent during `on_search`. In case of permissioned networks, this URL MUST match the `Subscriber.url` present on the respective entry in the Network Registry

### 5.3.2 Recommendations for BAPs

#### 5.3.2.1 Sending status updates

#### 5.3.2.2 Updating an order for energy service

#### 5.3.2.3 Cancelling a energy service aporderplication

#### 5.3.2.4 Real-time tracking

### 5.3.3 Example Workflow

### 5.3.4 Example Requests

An example of `status` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "status",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "chargezone-energy-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order_id": "6743e9e2-4fb5-487c-92b7"
  }
}
```

An example of `on_status` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "on_status",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "example-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order": {
      "id": "6743e9e2-4fb5-487c-92b7",
      "providers": {
        "id": "chargezone.in",
        "descriptor": {
          "name": "Chargezone",
          "short_desc": "Chargezone Technologies Pvt Ltd",
          "images": [
            {
              "url": "https://chargezone.in/images/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "pe-charging-01",
          "descriptor": {
            "code": "energy"
          },
          "price": {
            "value": "8",
            "currency": "INR/kWH"
          },
          "quantity": {
            "available": {
              "measure": {
                "value": "100",
                "unit": "kWh"
              }
            },
            "selected": {
              "measure": {
                "value": "4",
                "unit": "kWh"
              }
            }
          },
          "add_ons": [
            {
              "id": "pe-charging-01-addon-1",
              "descriptor": {
                "code": "add-on-item",
                "name": "Free car wash"
              },
              "price": {
                "value": "0",
                "currency": "INR"
              }
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "id": "1",
          "customer": {
            "person": {
              "name": "John Doe"
            },
            "contact": {
              "phone": "+91-9887766554"
            }
          },
          "type": "CHARGING",
          "state": {
            "descriptor": {
              "name": "vehicle 65% charged"
            }
          },
          "stops": [
            {
              "type": "start",
              "location": {
                "gps": "12.423423,77.325647"
              },
              "time": {
                "timestamp": "01-06-2023 10:00:00",
                "range": {
                  "start": "01-06-2023 10:00:00",
                  "end": "01-06-2023 10:10:00"
                }
              }
            },
            {
              "type": "end",
              "time": {
                "timestamp": "01-06-2023 10:30:00",
                "range": {
                  "start": "01-06-2023 10:30:00",
                  "end": "01-06-2023 10:40:00"
                }
              }
            }
          ],
          "tags": [
            {
              "descriptor": {
                "name": "Charging Point"
              },
              "list": [
                {
                  "descriptor": {
                    "name": "Charger type"
                  },
                  "value": "AC"
                },
                {
                  "descriptor": {
                    "name": "Connector type"
                  },
                  "value": "CCS2"
                },
                {
                  "descriptor": {
                    "name": "Power Rating"
                  },
                  "value": "greater than 50kW"
                },
                {
                  "descriptor": {
                    "name": "Availability"
                  },
                  "value": "Available"
                }
              ],
              "display": true
            }
          ]
        }
      ],
      "billing": {
        "email": "abc@example.com",
        "number": "+91-9876522222"
      },
      "quote": {
        "price": {
          "value": "32",
          "currency": "INR"
        },
        "breakup": [
          {
            "item": {
              "descriptor": {
                "name": "Estimated units consumed"
              },
              "quantity": {
                "selected": {
                  "measure": {
                    "value": "4",
                    "unit": "kWh"
                  }
                }
              }
            },
            "price": {
              "value": "32",
              "currency": "INR"
            }
          }
        ]
      },
      "payments": [
        {
          "type": "PRE-ORDER",
          "status": "PAID",
          "params": {
            "amount": "40",
            "currency": "INR"
          },
          "time": {
            "range": {
              "start": "2023-08-10T10:00:00Z",
              "end": "2023-08-10T10:30:00Z"
            }
          }
        }
      ],
      "cancellation_terms": [
        {
          "fulfillment_state": {
            "descriptor": {
              "code": "charging-start"
            }
          },
          "cancellation_fee": {
            "percentage": "30%"
          },
          "external_ref": {
            "mimetype": "text/html",
            "url": "https://chargezone.in/charge/tnc.html"
          }
        }
      ]
    }
  }
}
```

An example of `cancel` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "cancel",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "chargezone-energy-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order": {
      "cancellation_reason_id": "5",
      "descriptor": {
        "short_desc": "can't attend booking"
      },
      "order_id": "6743e9e2-4fb5-487c-92b7"
    }
  }
}
```

An example of `on_cancel` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "on_cancel",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "example-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order": {
      "id": "6743e9e2-4fb5-487c-92b7",
      "status": "CANCELLED",
      "providers": {
        "id": "chargezone.in",
        "descriptor": {
          "name": "Chargezone",
          "short_desc": "Chargezone Technologies Pvt Ltd",
          "images": [
            {
              "url": "https://chargezone.in/images/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "pe-charging-01",
          "descriptor": {
            "code": "energy"
          },
          "price": {
            "value": "8",
            "currency": "INR/kWH"
          },
          "quantity": {
            "available": {
              "measure": {
                "value": "100",
                "unit": "kWh"
              }
            },
            "selected": {
              "measure": {
                "value": "4",
                "unit": "kWh"
              }
            }
          },
          "add_ons": [
            {
              "id": "pe-charging-01-addon-1",
              "descriptor": {
                "code": "add-on-item",
                "name": "Free car wash"
              },
              "price": {
                "value": "0",
                "currency": "INR"
              }
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "id": "1",
          "customer": {
            "person": {
              "name": "John Doe"
            },
            "contact": {
              "phone": "+91-9887766554"
            }
          },
          "type": "CHARGING",
          "state": {
            "descriptor": {
              "code": "order-cancelled"
            }
          },
          "stops": [
            {
              "time": {
                "range": {
                  "start": "10:00",
                  "end": "10:30"
                }
              }
            }
          ],
          "tags": [
            {
              "descriptor": {
                "name": "Charging Point"
              },
              "list": [
                {
                  "descriptor": {
                    "name": "Charger type"
                  },
                  "value": "AC"
                },
                {
                  "descriptor": {
                    "name": "Connector type"
                  },
                  "value": "CCS2"
                },
                {
                  "descriptor": {
                    "name": "Power Rating"
                  },
                  "value": "greater than 50kW"
                },
                {
                  "descriptor": {
                    "name": "Availability"
                  },
                  "value": "Available"
                }
              ],
              "display": true
            }
          ]
        }
      ],
      "billing": {
        "email": "abc@example.com",
        "number": "+91-9876522222"
      },
      "quote": {
        "price": {
          "value": "-32",
          "currency": "INR"
        },
        "breakup": [
          {
            "item": {
              "descriptor": {
                "name": "payment refund"
              },
              "quantity": {
                "selected": {
                  "measure": {
                    "value": "4",
                    "unit": "kWh"
                  }
                }
              }
            },
            "price": {
              "value": "-32",
              "currency": "INR"
            }
          }
        ]
      },
      "payments": [
        {
          "type": "PRE-ORDER",
          "status": "PAID",
          "params": {
            "amount": "40",
            "currency": "INR"
          },
          "time": {
            "range": {
              "start": "2023-08-10T10:00:00Z",
              "end": "2023-08-10T10:30:00Z"
            }
          }
        }
      ],
      "cancellation_terms": [
        {
          "fulfillment_state": {
            "descriptor": {
              "code": "charging-start"
            }
          },
          "cancellation_fee": {
            "percentage": "30%"
          },
          "external_ref": {
            "mimetype": "text/html",
            "url": "https://chargezone.in/charge/tnc.html"
          }
        }
      ]
    }
  }
}
```

An example of `update` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "update",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "chargezone-energy-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "update_target": "order.fulfillments[0].state",
    "order": {
      "fulfillments": [
        {
          "id": "1",
          "type": "CHARGING",
          "state": {
            "descriptor": {
              "code": "start-charging"
            }
          }
        }
      ]
    }
  }
}
```

An example of `on_update` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "on_update",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "example-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "order": {
      "id": "6743e9e2-4fb5-487c-92b7",
      "providers": {
        "id": "chargezone.in",
        "descriptor": {
          "name": "Chargezone",
          "short_desc": "Chargezone Technologies Pvt Ltd",
          "images": [
            {
              "url": "https://chargezone.in/images/logo.png"
            }
          ]
        }
      },
      "items": [
        {
          "id": "pe-charging-01",
          "descriptor": {
            "code": "energy"
          },
          "price": {
            "value": "8",
            "currency": "INR/kWH"
          },
          "quantity": {
            "available": {
              "measure": {
                "value": "100",
                "unit": "kWh"
              }
            },
            "selected": {
              "measure": {
                "value": "4",
                "unit": "kWh"
              }
            }
          },
          "add_ons": [
            {
              "id": "pe-charging-01-addon-1",
              "descriptor": {
                "code": "add-on-item",
                "name": "Free car wash"
              },
              "price": {
                "value": "0",
                "currency": "INR"
              }
            }
          ]
        }
      ],
      "fulfillments": [
        {
          "id": "1",
          "customer": {
            "person": {
              "name": "John Doe"
            },
            "contact": {
              "phone": "+91-9887766554"
            }
          },
          "type": "CHARGING",
          "state": {
            "descriptor": {
              "code": "charging-started"
            }
          },
          "stops": [
            {
              "type": "start",
              "location": {
                "gps": "12.423423,77.325647"
              },
              "time": {
                "timestamp": "01-06-2023 10:00:00",
                "range": {
                  "start": "01-06-2023 10:00:00",
                  "end": "01-06-2023 10:10:00"
                }
              }
            },
            {
              "type": "end",
              "time": {
                "timestamp": "01-06-2023 10:30:00",
                "range": {
                  "start": "01-06-2023 10:30:00",
                  "end": "01-06-2023 10:40:00"
                }
              }
            }
          ],
          "tags": [
            {
              "descriptor": {
                "name": "Charging Point"
              },
              "list": [
                {
                  "descriptor": {
                    "name": "Charger type"
                  },
                  "value": "AC"
                },
                {
                  "descriptor": {
                    "name": "Connector type"
                  },
                  "value": "CCS2"
                },
                {
                  "descriptor": {
                    "name": "Power Rating"
                  },
                  "value": "greater than 50kW"
                },
                {
                  "descriptor": {
                    "name": "Availability"
                  },
                  "value": "Available"
                }
              ],
              "display": true
            }
          ]
        }
      ],
      "billing": {
        "email": "abc@example.com",
        "number": "+91-9876522222"
      },
      "quote": {
        "price": {
          "value": "40",
          "currency": "INR"
        },
        "breakup": [
          {
            "item": {
              "descriptor": {
                "name": "Estimated units consumed"
              },
              "quantity": {
                "selected": {
                  "measure": {
                    "value": "4",
                    "unit": "kWh"
                  }
                }
              }
            },
            "price": {
              "value": "32",
              "currency": "INR"
            }
          }
        ]
      },
      "payments": [
        {
          "type": "PRE-ORDER",
          "status": "PAID",
          "params": {
            "amount": "40",
            "currency": "INR"
          },
          "time": {
            "range": {
              "start": "2023-08-10T10:00:00Z",
              "end": "2023-08-10T10:30:00Z"
            }
          }
        }
      ],
      "cancellation_terms": [
        {
          "fulfillment_state": {
            "descriptor": {
              "code": "charging-start"
            }
          },
          "cancellation_fee": {
            "percentage": "30%"
          },
          "external_ref": {
            "mimetype": "text/html",
            "url": "https://chargezone.in/charge/tnc.html"
          }
        }
      ]
    }
  }
}
```

## Post-fulfillment

This section contains recommendations for implementing the APIs after fulfilling a energy service

### 5.4.1 Recommendations for BPPs

#### 5.4.1.1 Rating and Feedback

- REQUIRED. The BPP MUST implement the `rating` endpoint on the url specified in URL specified in the `context.bpp_uri` field sent during `on_search`. In case of permissioned networks, this URL MUST match the `Subscriber.url` present on the respective entry in the Network Registry
- REQUIRED. The BPP MUST implement the `get_rating_categories` endpoint on the url specified in URL specified in the `context.bpp_uri` field sent during `on_search`. In case of permissioned networks, this URL MUST match the `Subscriber.url` present on the respective entry in the Network Registry

#### 5.4.1.2 Providing Support

- REQUIRED. The BPP MUST implement the `support` endpoint on the url specified in URL specified in the `context.bpp_uri` field sent during `on_search`. In case of permissioned networks, this URL MUST match the `Subscriber.url` present on the respective entry in the Network Registry

### 5.4.2 Recommendations for BAPs

#### 5.4.2.1 Rating and Feedback

#### 5.4.2.2 Providing Support

### 5.4.3 Example Workflow

### 5.4.4 Example Requests

An example of `rating` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "rating",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "chargezone-energy-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "ratings": [
      {
        "id": "6743e9e2-4fb5-487c-92b7",
        "rating_category": "charger",
        "value": "5"
      }
    ]
  }
}
```

An example of `on_rating` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "on_rating",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "chargezone-energy-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "feedback_form": {
        "form": {
          "url": "https://api.example-bpp.com/pilot/bpp/feedback/portal"
        },
        "required": "false"
    }
  }
}
```

An example of `support` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "support",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "chargezone-energy-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "support": {
      "ref_id": "6743e9e2-4fb5-487c-92b7",
      "phone": "+919876543210",
      "email": "john.doe@gmail.com"
    }
  }
}
```

An example of `on_support` request

```json
{
  "context": {
    "domain": "dent:0.1.0",
    "action": "on_support",
    "location": {
      "country": {
        "code": "IND"
      },
      "city": {
        "code": "std:080"
      }
    },
    "version": "1.1.0",
    "bap_id": "example-bap.com",
    "bap_uri": "https://api.example-bap.com/pilot/bap/energy/v1",
    "bpp_id": "chargezone-energy-bpp.com",
    "bpp_uri": "https://api.example-bpp.com/pilot/bpp/",
    "transaction_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "message_id": "6743e9e2-4fb5-487c-92b7-13ba8018f176",
    "timestamp": "2023-07-16T04:41:16Z"
  },
  "message": {
    "support": {
      "ref_id": "6743e9e2-4fb5-487c-92b7",
      "phone": "1800 1080",
      "email": "customer.care@chargezone.com",
      "url": "https://www.chargezone.com/helpdesk"
    }
  }
}
```
