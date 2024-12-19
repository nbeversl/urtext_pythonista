import urtext.syntax as syntax
import re

class UrtextSyntax:

	def __init__(self, theme):
		
		self.theme = theme
		self.name = 'Urtext'

		node_link_or_pointer_syntax = {
			'pattern': syntax.node_link_or_pointer_c,       
			'self': {
					'font' : theme['font']['bold'],
				},
			'scoped' : {
				'link_titles' : { 
					'pattern': re.compile('([^\|>\n\r]+)', flags=re.DOTALL),
					'self': {
						'color': theme['node_pointers']
						}
					},
				'action_modifier': { 
					'pattern': syntax.node_link_modifiers_regex_c['action'],
					'self': {
						'color': theme['node_link_modifier_action']
					}
				},
			   	'missing_modifier' : {
					'pattern': syntax.node_link_modifiers_regex_c['missing'],
					'self': {
						'color': theme['node_link_modifier_missing']
					}
				},
			},
		}

		file_link_syntax = {
			'pattern': syntax.file_link_c,       
			'self': {
				'font' : theme['font']['bold'],
			},
			'scoped': {
				'file_modifier': {
					'pattern': re.compile(syntax.file_link_modifiers['file']),
					'self': {
						'color': theme['file_link_modifier_file']
					}
				},
				'file_missing_modifier': {
					'pattern': re.compile(re.escape(syntax.file_link_modifiers['missing'])),
					'self': {
						'color': theme['file_link_modifier_missing']
					}
				},
			}
		}

		self.syntax = {
   
			'dynamic_def': {
				'pattern': syntax.dynamic_def_c,
				'self': {
					   'color': theme['dynamic_definition_wrapper'],
					   'font' : theme['font']['bold italic'],
					   },
				'scoped' : {
					'function_name' : { 
						'pattern': syntax.function_c, 
						'self': {
							'color' : theme['function_names'],
							'font' : theme['font']['bold'],
						},
						'scoped' : {
							'flag': {
								'pattern': syntax.dd_flags_c, 
								'self' : {
									'color' : theme['flag'] 
									},
							},
							'format_key': {
								'pattern': syntax.format_key_c,
								'self': {
									'color': theme['format_key'],
									'font' : theme['font']['bold'],
								}
							},
							'key_op_value': {
								'pattern': syntax.dd_key_op_value_c,
								'self': {
									'groups': {
										1 : theme['function_keys'],
										2 : theme['function_operators'],
										3 : theme['function_values'],
									}
								}
							},
							# 'key_with_opt_flag': {
							# 	'pattern': syntax.dd_key_with_opt_flags,
							# 	'self': {
							# 		'groups': {
							# 			2 : theme['dd_key'],
							# 			# 2 : theme['dd_flag'],
							# 		}
							# 	}
							# }

						}
					},
				},
			},
			'node_link_or_pointer':	node_link_or_pointer_syntax,
			'file_link_syntax': file_link_syntax,
			'metadata_key' : {

				'pattern': syntax.sh_metadata_key_c, 
				'self': {
					'color': theme['keys'],
					'font': theme['font']['regular'],
					},
			},
			'metadata_flag': {
				'pattern' : syntax.metadata_flags_c,
				'self' : {
					'font' : theme['metadata_flags']
				}
			},
			'metadata_assigner': {  
				'pattern': syntax.metadata_assigner_c,
				'self' : {
					'color' : theme['metadata_assigner'] 
				},
			},
			'metadata_values': {
				'pattern': syntax.sh_metadata_values_c,
				'self': {
					'color' : theme['metadata_values'] 
				},

				'scoped': { 
					'metadata_separator': {
						'pattern':syntax.metadata_separator_pattern_c, 
						'self': {
							'color': theme['metadata_separator'] 
							}  
					},
				}
			},
			'hash_meta': {
				'pattern':syntax.hash_meta_c,
				'self': {
					'font' : theme['font']['bold']
				}
			},   
			'timestamp' : {
				'pattern': syntax.timestamp_c,
				'self': {
					'color': theme['timestamp'] 
					},
			},
			'title': {  
				# SLOW
				'pattern': re.compile(r'(?<!\{)([\w\s\d\']+?\s_)(?=\s|$)'),
				'self': {
					'font' : theme['font']['bold']
				},
			},
			'opening_wrapper' : {
				'pattern': syntax.opening_wrapper_c,
				'self' : {
					'color' : theme['error_messages']
				},
			},
			'closing_bracket': {
				'pattern': syntax.closing_wrapper_c,
				'self' : {
					'color' : theme['error_messages']
				},
			},
			'escape_wrapper' : {
				'pattern': re.compile('`.*?`'),
				'self' : {
					'color' : theme['error_messages']
				},
			},
		}
