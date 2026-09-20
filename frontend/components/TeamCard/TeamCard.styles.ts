import { StyleSheet, ViewStyle, TextStyle } from 'react-native';

interface Styles {
  card: ViewStyle;
  content: ViewStyle;
  iconContainer: ViewStyle;
  symbolicText: TextStyle;
  info: ViewStyle;
  name: TextStyle;
  shortName: TextStyle;
  rankBadge: ViewStyle;
  rankText: TextStyle;
  stripe: ViewStyle;
}

export const styles = StyleSheet.create<Styles>({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginHorizontal: 16,
    marginBottom: 12,
    flexDirection: 'row',
    overflow: 'hidden',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    borderLeftWidth: 6,
  },
  content: {
    flex: 1,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    width: 52,
    height: 52,
    borderRadius: 26,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
    borderWidth: 1,
    borderColor: '#f0f0f0',
  },
  symbolicText: {
    fontSize: 10,
    fontWeight: 'bold',
    position: 'absolute',
    bottom: -4,
  },
  info: {
    flex: 1,
  },
  name: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  shortName: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  rankBadge: {
    backgroundColor: '#f0f2f5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  rankText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#333',
  },
  stripe: {
    width: 4,
    height: '100%',
    opacity: 0.2,
  },
});