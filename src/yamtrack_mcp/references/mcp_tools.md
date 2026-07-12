## MCP Tools Reference
[
  {
    "server": "yamtrack",
    "name": "search_media",
    "description": "Search for media across external providers.\n\n    Supported media types: tv, movie, anime, manga, game, book, comic, boardgame.\n    ",
    "inputSchema": {
      "properties": {
        "query": {
          "title": "Query",
          "type": "string"
        },
        "media_type": {
          "default": "tv",
          "title": "Media Type",
          "type": "string"
        },
        "page": {
          "default": 1,
          "title": "Page",
          "type": "integer"
        },
        "source": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Source"
        }
      },
      "required": [
        "query"
      ],
      "title": "search_mediaArguments",
      "type": "object"
    }
  },
  {
    "server": "yamtrack",
    "name": "get_details",
    "description": "Get metadata details for a media item from an external provider.",
    "inputSchema": {
      "properties": {
        "source": {
          "title": "Source",
          "type": "string"
        },
        "media_type": {
          "title": "Media Type",
          "type": "string"
        },
        "media_id": {
          "title": "Media Id",
          "type": "string"
        },
        "season_number": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Season Number"
        }
      },
      "required": [
        "source",
        "media_type",
        "media_id"
      ],
      "title": "get_detailsArguments",
      "type": "object"
    }
  },
  {
    "server": "yamtrack",
    "name": "list_tracked_media",
    "description": "List media tracked by the authenticated user.\n\n    Status options: All, Completed, In progress, Planning, Paused, Dropped.\n    ",
    "inputSchema": {
      "properties": {
        "media_type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Media Type"
        },
        "status": {
          "default": "All",
          "title": "Status",
          "type": "string"
        },
        "sort": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Sort"
        },
        "search": {
          "default": "",
          "title": "Search",
          "type": "string"
        }
      },
      "title": "list_tracked_mediaArguments",
      "type": "object"
    }
  },
  {
    "server": "yamtrack",
    "name": "create_entry",
    "description": "Start tracking a new media item from an external provider.\n\n    Status defaults to \"Completed\" if omitted. Score is 0-10.\n    ",
    "inputSchema": {
      "properties": {
        "media_id": {
          "title": "Media Id",
          "type": "string"
        },
        "source": {
          "title": "Source",
          "type": "string"
        },
        "media_type": {
          "title": "Media Type",
          "type": "string"
        },
        "status": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Status"
        },
        "score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Score"
        },
        "progress": {
          "default": 0,
          "title": "Progress",
          "type": "integer"
        },
        "notes": {
          "default": "",
          "title": "Notes",
          "type": "string"
        }
      },
      "required": [
        "media_id",
        "source",
        "media_type"
      ],
      "title": "create_entryArguments",
      "type": "object"
    }
  },
  {
    "server": "yamtrack",
    "name": "update_entry",
    "description": "Update status, score, progress, or notes for a tracked media item.",
    "inputSchema": {
      "properties": {
        "media_type": {
          "title": "Media Type",
          "type": "string"
        },
        "instance_id": {
          "title": "Instance Id",
          "type": "integer"
        },
        "status": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Status"
        },
        "score": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Score"
        },
        "progress": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Progress"
        },
        "notes": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Notes"
        }
      },
      "required": [
        "media_type",
        "instance_id"
      ],
      "title": "update_entryArguments",
      "type": "object"
    }
  },
  {
    "server": "yamtrack",
    "name": "update_progress",
    "description": "Increase or decrease progress on a media item.\n\n    Operation must be 'increase' or 'decrease'.\n    ",
    "inputSchema": {
      "properties": {
        "media_type": {
          "title": "Media Type",
          "type": "string"
        },
        "instance_id": {
          "title": "Instance Id",
          "type": "integer"
        },
        "operation": {
          "title": "Operation",
          "type": "string"
        }
      },
      "required": [
        "media_type",
        "instance_id",
        "operation"
      ],
      "title": "update_progressArguments",
      "type": "object"
    }
  },
  {
    "server": "yamtrack",
    "name": "update_score",
    "description": "Update the score (0-10) for a tracked media item.",
    "inputSchema": {
      "properties": {
        "media_type": {
          "title": "Media Type",
          "type": "string"
        },
        "instance_id": {
          "title": "Instance Id",
          "type": "integer"
        },
        "score": {
          "title": "Score",
          "type": "number"
        }
      },
      "required": [
        "media_type",
        "instance_id",
        "score"
      ],
      "title": "update_scoreArguments",
      "type": "object"
    }
  },
  {
    "server": "yamtrack",
    "name": "get_home",
    "description": "Get dashboard data: in-progress and planning media.",
    "inputSchema": {
      "properties": {
        "sort": {
          "default": "upcoming",
          "title": "Sort",
          "type": "string"
        }
      },
      "title": "get_homeArguments",
      "type": "object"
    }
  },
  {
    "server": "yamtrack",
    "name": "get_statistics",
    "description": "Get aggregated statistics for the authenticated user.\n\n    Dates in YYYY-MM-DD format. Use 'all'/'all' for no filter.\n    Defaults to last 365 days.\n    ",
    "inputSchema": {
      "properties": {
        "start_date": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Start Date"
        },
        "end_date": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "End Date"
        }
      },
      "title": "get_statisticsArguments",
      "type": "object"
    }
  },
  {
    "server": "yamtrack",
    "name": "get_history",
    "description": "Get change history for a tracked media item.",
    "inputSchema": {
      "properties": {
        "source": {
          "title": "Source",
          "type": "string"
        },
        "media_type": {
          "title": "Media Type",
          "type": "string"
        },
        "media_id": {
          "title": "Media Id",
          "type": "string"
        },
        "season_number": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Season Number"
        },
        "episode_number": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Episode Number"
        }
      },
      "required": [
        "source",
        "media_type",
        "media_id"
      ],
      "title": "get_historyArguments",
      "type": "object"
    }
  }
]